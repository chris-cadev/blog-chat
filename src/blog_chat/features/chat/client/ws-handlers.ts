const MAX_CHARS = 280;
const RECONNECT_BASE_DELAY = 1000;
const RECONNECT_MAX_DELAY = 30000;
const SYNC_INTERVAL = 60000;
const HEARTBEAT_TIMEOUT = 90000;

let ws: WebSocket | null = null;
let wsUrl = "";
let reconnectAttempts = 0;
let reconnectTimer: number | null = null;
let manuallyClosed = false;
let isSending = false;
let pendingDraft = "";
let timezoneCookieSet = false;
let chatInited = false;
let lastReceivedAt = 0;
let historyLoaded = false;
let currentMessageIds: string[] = [];
let forceHistoryReload = false;

function getTimezone(): string {
  return Intl.DateTimeFormat().resolvedOptions().timeZone;
}

function setTimezoneCookie(tz: string) {
  const expires = new Date();
  expires.setFullYear(expires.getFullYear() + 1);
  document.cookie = `chat_timezone=${tz};expires=${expires.toUTCString()};path=/;SameSite=Lax`;
}

function ensureTimezoneCookie() {
  if (timezoneCookieSet) return;
  const tz = getTimezone();
  if (tz) {
    setTimezoneCookie(tz);
    timezoneCookieSet = true;
  }
}

function formatRelativeTime(isoString: string): string {
  const date = new Date(isoString);
  const now = new Date();
  const diffSec = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffSec < 60) return `${Math.max(diffSec, 0)}s ago`;
  if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`;
  if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}h ago`;
  return `${Math.floor(diffSec / 86400)}d ago`;
}

function updateTimestamps() {
  const times = document.querySelectorAll("#chat-messages time");
  times.forEach((time) => {
    const iso = time.getAttribute("datetime");
    if (iso) {
      time.textContent = formatRelativeTime(iso);
    }
  });
}

function updateCharCount() {
  const input = document.getElementById("chat-input") as HTMLInputElement;
  const counter = document.getElementById("char-count");
  if (input && counter) {
    const len = input.value.length;
    counter.textContent = `${len}/${MAX_CHARS}`;
    counter.classList.toggle("text-error", len > MAX_CHARS);
    counter.classList.toggle("text-base-content/50", len <= MAX_CHARS);
  }
  updateInputHint();
}

function updateInputHint() {
  const input = document.getElementById("chat-input") as HTMLInputElement;
  const hint = document.getElementById("chat-input-hint");
  const status = document.getElementById("chat-status");
  if (!input || !hint || !status) return;
  const statusHidden = status.classList.contains("hidden");
  hint.classList.toggle("hidden", input.value.length > 0 || !statusHidden);
}

function setLoadingState(loading: boolean) {
  const sendBtn = document.getElementById("send-btn") as HTMLButtonElement;
  const input = document.getElementById("chat-input") as HTMLInputElement;
  if (sendBtn) {
    sendBtn.disabled = loading;
    sendBtn.innerHTML = loading
      ? '<span class="loading loading-spinner loading-sm"></span>'
      : "Send";
  }
  if (input) {
    input.disabled = loading;
  }
}

function showStatus(message: string, show = true) {
  const status = document.getElementById("chat-status");
  if (!status) return;
  status.textContent = show ? message : "";
  status.classList.toggle("hidden", !show);
  updateInputHint();
}

function setConnectionState(state: "connecting" | "connected" | "reconnecting" | "disconnected") {
  if (state === "connected") {
    showStatus("");
  } else if (state === "reconnecting") {
    showStatus("Reconnecting…");
  } else if (state === "connecting") {
    showStatus("Connecting…");
  } else {
    showStatus("Disconnected");
  }
}

function showEmptyState(show: boolean) {
  const empty = document.getElementById("chat-empty");
  if (empty) {
    empty.classList.toggle("hidden", !show);
  }
}

function isNearTop(): boolean {
  const container = document.getElementById("chat-messages");
  if (!container) return true;
  const threshold = 100;
  return container.scrollTop <= threshold;
}

function scrollToTop(smooth = false) {
  const container = document.getElementById("chat-messages");
  if (container) {
    container.scrollTo({
      top: 0,
      behavior: smooth ? "smooth" : "auto",
    });
  }
}

function createScrollButton(): HTMLElement {
  const btn = document.createElement("button");
  btn.id = "scroll-to-top";
  btn.className =
    "btn btn-sm btn-primary fixed bottom-24 right-8 z-50 shadow-lg";
  btn.textContent = "New messages";
  btn.addEventListener("click", () => {
    scrollToTop(true);
    btn.remove();
  });
  return btn;
}

function resetSendingState() {
  if (isSending) {
    isSending = false;
    pendingDraft = "";
    setLoadingState(false);
  }
}

export function initChat() {
  if (chatInited) return;
  chatInited = true;

  ensureTimezoneCookie();

  const room = document.body.getAttribute("data-room") || "offtopic";
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  wsUrl = `${protocol}//${window.location.host}/ws/chat?room=${room}`;

  bindChangeUsername();
  bindStarterPrompts();
  initGlow();
  connect();

  const input = document.getElementById("chat-input") as HTMLInputElement;
  const sendBtn = document.getElementById("send-btn");

  if (input && sendBtn) {
    input.addEventListener("input", updateCharCount);
    sendBtn.addEventListener("click", () => sendMessage(input));
    input.addEventListener("keypress", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage(input);
      }
    });
    updateCharCount();
  }

  setInterval(updateTimestamps, 30000);
  window.setInterval(requestSync, SYNC_INTERVAL);
  setInterval(checkConnectionLiveness, 30000);
}

function getUsernameColor(username: string): string {
  let hash = 0x811c9dc5;
  const bytes = new TextEncoder().encode(username);
  for (let i = 0; i < bytes.length; i++) {
    hash ^= bytes[i];
    hash = (hash * 0x01000193) >>> 0;
  }
  return `hsl(${hash % 360}, 70%, 45%)`;
}

let usernameEditActive = false;

function bindChangeUsername() {
  const editBtn = document.getElementById("change-username-btn");
  const nameBtn = document.getElementById("username-edit-btn");
  const input = document.getElementById("username-input") as HTMLInputElement;
  if (!editBtn || !nameBtn || !input) return;

  const room = document.body.getAttribute("data-room") || "offtopic";

  const enterEdit = () => {
    if (usernameEditActive) return;
    usernameEditActive = true;
    nameBtn.style.display = "none";
    editBtn.style.display = "none";
    const current = nameBtn.textContent || "";
    input.value = current;
    input.style.color = getUsernameColor(current);
    input.classList.remove("hidden");
    input.focus();
    input.select();
    window.setTimeout(() => {
      if (!usernameEditActive) return;
      const expected = nameBtn.textContent || "";
      if (input.value !== expected) {
        input.value = expected;
        input.style.color = getUsernameColor(expected);
        input.select();
      }
    }, 0);
  };

  const cancelEdit = () => {
    if (!usernameEditActive) return;
    usernameEditActive = false;
    input.classList.add("hidden");
    nameBtn.style.display = "";
    editBtn.style.display = "";
  };

  const save = async () => {
    if (!usernameEditActive) return;
    const value = input.value.trim();
    const current = nameBtn.textContent || "";
    if (!value || value === current) {
      cancelEdit();
      return;
    }
    try {
      const res = await fetch(
        `/api/set-username?room=${encodeURIComponent(room)}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username: value }),
        }
      );
      if (!res.ok) {
        input.classList.add("text-error");
        window.setTimeout(() => input.classList.remove("text-error"), 1500);
        input.focus();
        return;
      }
      nameBtn.textContent = value;
      nameBtn.style.color = getUsernameColor(value);
      document
        .getElementById("chat-messages")
        ?.setAttribute("data-username", value);
      cancelEdit();
      forceReconnect();
    } catch {
      cancelEdit();
    }
  };

  editBtn.addEventListener("click", enterEdit);
  nameBtn.addEventListener("click", enterEdit);
  input.addEventListener("input", () => {
    input.style.color = getUsernameColor(input.value);
  });
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      save();
    } else if (e.key === "Escape") {
      cancelEdit();
    }
  });
  input.addEventListener("blur", () => {
    save();
  });
}

function bindStarterPrompts() {
  const input = document.getElementById("chat-input") as HTMLInputElement;
  const starterButtons = document.querySelectorAll<HTMLButtonElement>("[data-starter]");
  starterButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      if (!input) return;
      input.value = btn.dataset.starterMessage || btn.dataset.starter || "";
      updateCharCount();
      input.focus();
    });
  });
}

function initGlow() {
  let shown = false;
  try {
    shown = sessionStorage.getItem("chat_attention_shown") === "1";
  } catch {
    shown = false;
  }
  if (shown) return;

  const container = document.getElementById("chat-messages");
  if (!container) return;
  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        observer.disconnect();
        window.setTimeout(() => {
          try {
            sessionStorage.setItem("chat_attention_shown", "1");
          } catch {
            /* ignore storage restrictions */
          }
          container.classList.add("chat-glow");
          const inputGroup = document.getElementById("chat-input-group");
          if (inputGroup) {
            inputGroup.classList.add("chat-glow-ring");
          }
          const newest = container.firstElementChild;
          const bubble = newest?.querySelector(".chat-bubble");
          if (bubble) {
            bubble.classList.add("chat-shimmer");
          }
        }, 1500);
        return;
      }
    },
    { threshold: 0 }
  );
  observer.observe(container);
}

function connect() {
  manuallyClosed = false;
  setConnectionState("connecting");

  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    reconnectAttempts = 0;
    setConnectionState("connected");
  };

  ws.onmessage = (event) => {
    let data: any;
    try {
      data = JSON.parse(event.data);
    } catch {
      return;
    }
    lastReceivedAt = Date.now();

    if (data.type === "error") {
      handleError(data);
      return;
    }

    if (data.type === "history") {
      loadChatHistory(data, forceHistoryReload);
      forceHistoryReload = false;
    } else if (data.type === "message") addMessage(data);
    else if (data.type === "presence") updatePresence(data.count);
    else if (data.type === "refresh") {
      forceHistoryReload = true;
      requestSync();
    }
  };

  ws.onclose = () => {
    setConnectionState("disconnected");
    resetSendingState();
    if (!manuallyClosed) scheduleReconnect();
  };
}

function forceReconnect() {
  forceHistoryReload = true;
  if (ws) {
    ws.onclose = null;
    ws.close();
    ws = null;
  }
  reconnectAttempts = 0;
  connect();
}

function scheduleReconnect() {
  if (reconnectTimer !== null) return;
  const delay = Math.min(
    RECONNECT_BASE_DELAY * 2 ** reconnectAttempts,
    RECONNECT_MAX_DELAY
  );
  reconnectAttempts += 1;
  setConnectionState("reconnecting");
  reconnectTimer = window.setTimeout(() => {
    reconnectTimer = null;
    connect();
  }, delay);
}

function loadChatHistory(data: any, force = false) {
  const container = document.getElementById("chat-messages");
  if (!container) return;

  const incomingIds = (data.messages || []).map((m: any) => String(m.id));
  if (!force && historyLoaded && isPrefixOf(currentMessageIds, incomingIds)) {
    return;
  }
  currentMessageIds = incomingIds;

  container.innerHTML = "";
  if (data.messages.length === 0) {
    showEmptyState(true);
  } else {
    showEmptyState(false);
    data.messages.forEach((msg: any) => addHistoryMessage(msg));
    scrollToTop();
  }
  historyLoaded = true;
}

function isPrefixOf(current: string[], incoming: string[]): boolean {
  if (incoming.length > current.length) return false;
  for (let i = 0; i < incoming.length; i++) {
    if (current[i] !== incoming[i]) return false;
  }
  return true;
}

function requestSync() {
  if (!ws || ws.readyState !== WebSocket.OPEN) return;
  ws.send(JSON.stringify({ type: "sync" }));
}

function updatePresence(count: number) {
  const el = document.getElementById("chat-presence");
  if (!el) return;
  const label = el.dataset.label || "";
  el.textContent = `${count} ${label}`.trim();
}

function checkConnectionLiveness() {
  if (!ws || ws.readyState !== WebSocket.OPEN) return;
  if (lastReceivedAt > 0 && Date.now() - lastReceivedAt > HEARTBEAT_TIMEOUT) {
    ws.close();
  }
}

function addHistoryMessage(msg: any) {
  const container = document.getElementById("chat-messages");
  if (!container) return;

  showEmptyState(false);
  container.insertAdjacentHTML("beforeend", msg.html);

  const inserted = container.lastElementChild;
  inserted?.querySelectorAll("time").forEach((time) => {
    if (msg.timestamp) {
      time.setAttribute("datetime", msg.timestamp);
    }
  });
}

function sendMessage(input: HTMLInputElement) {
  const text = input.value.trim();
  if (!text || text.length > MAX_CHARS) return;
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    showStatus("Not connected. Reconnecting…");
    return;
  }
  if (isSending) return;

  isSending = true;
  pendingDraft = text;
  setLoadingState(true);

  ws.send(text);
  input.value = "";
  updateCharCount();
}

function handleError(data: any) {
  isSending = false;
  setLoadingState(false);

  const input = document.getElementById("chat-input") as HTMLInputElement;
  if (pendingDraft) {
    input.value = pendingDraft;
    pendingDraft = "";
    updateCharCount();
  }
  showStatus(data.message || "Something went wrong. Try again.");
  if (input) input.focus();

  window.setTimeout(() => {
    const status = document.getElementById("chat-status");
    if (status && !status.classList.contains("hidden")) {
      const connected = ws && ws.readyState === WebSocket.OPEN;
      setConnectionState(connected ? "connected" : "reconnecting");
    }
  }, 5000);
}

function addMessage(data: any) {
  if (isSending) {
    isSending = false;
    pendingDraft = "";
    setLoadingState(false);
  }

  const container = document.getElementById("chat-messages");
  if (!container) return;

  if (data.id != null) currentMessageIds.unshift(String(data.id));

  showEmptyState(false);
  const wasNearTop = isNearTop();

  const temp = document.createElement("div");
  temp.innerHTML = data.html;
  const msgEl = temp.firstElementChild;

  const timeEl = msgEl?.querySelector("time");
  if (timeEl && data.timestamp) {
    timeEl.setAttribute("datetime", data.timestamp);
  }

  if (msgEl) {
    msgEl.classList.add("chat-bubble-enter");
    container.prepend(msgEl);
  }

  if (wasNearTop) {
    scrollToTop();
  } else {
    const existingBtn = document.getElementById("scroll-to-top");
    if (!existingBtn) {
      document.body.appendChild(createScrollButton());
    }
  }
}
