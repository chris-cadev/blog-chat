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
let syncTimer: number | null = null;

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

function isNearBottom(): boolean {
  const container = document.getElementById("chat-messages");
  if (!container) return true;
  const threshold = 100;
  return (
    container.scrollHeight - container.scrollTop - container.clientHeight <=
    threshold
  );
}

function scrollToBottom(smooth = false) {
  const container = document.getElementById("chat-messages");
  if (container) {
    container.scrollTo({
      top: container.scrollHeight,
      behavior: smooth ? "smooth" : "auto",
    });
  }
}

function createScrollButton(): HTMLElement {
  const btn = document.createElement("button");
  btn.id = "scroll-to-bottom";
  btn.className =
    "btn btn-sm btn-primary fixed bottom-24 right-8 z-50 shadow-lg";
  btn.textContent = "New messages";
  btn.addEventListener("click", () => {
    scrollToBottom(true);
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

  bindUsernameRefresh();
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
  syncTimer = window.setInterval(requestSync, SYNC_INTERVAL);
  setInterval(checkConnectionLiveness, 30000);
}

function bindUsernameRefresh() {
  document.body.addEventListener("htmx:afterSwap", () => {
    const section = document.getElementById("username-section");
    if (section && !section.querySelector("form")) {
      window.location.reload();
    }
  });
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

    if (data.type === "history") loadChatHistory(data);
    else if (data.type === "message") addMessage(data);
    else if (data.type === "refresh") requestSync();
  };

  ws.onclose = () => {
    setConnectionState("disconnected");
    resetSendingState();
    if (!manuallyClosed) scheduleReconnect();
  };
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

function loadChatHistory(data: any) {
  const container = document.getElementById("chat-messages");
  if (!container) return;

  const incomingIds = (data.messages || []).map((m: any) => String(m.id));
  if (historyLoaded && isSuffixOf(currentMessageIds, incomingIds)) {
    return;
  }
  currentMessageIds = incomingIds;

  container.innerHTML = "";
  if (data.messages.length === 0) {
    showEmptyState(true);
  } else {
    showEmptyState(false);
    data.messages.forEach((msg: any) => addHistoryMessage(msg));
    scrollToBottom();
  }
  historyLoaded = true;
}

function isSuffixOf(current: string[], incoming: string[]): boolean {
  if (incoming.length > current.length) return false;
  const start = current.length - incoming.length;
  for (let i = 0; i < incoming.length; i++) {
    if (current[start + i] !== incoming[i]) return false;
  }
  return true;
}

function requestSync() {
  if (!ws || ws.readyState !== WebSocket.OPEN) return;
  ws.send(JSON.stringify({ type: "sync" }));
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

  const timeEl = container.lastElementChild?.querySelector("time");
  if (timeEl && msg.timestamp) {
    timeEl.setAttribute("datetime", msg.timestamp);
  }
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

  if (data.id != null) currentMessageIds.push(String(data.id));

  showEmptyState(false);
  const wasNearBottom = isNearBottom();

  const temp = document.createElement("div");
  temp.innerHTML = data.html;
  const msgEl = temp.firstElementChild;

  const timeEl = msgEl?.querySelector("time");
  if (timeEl && data.timestamp) {
    timeEl.setAttribute("datetime", data.timestamp);
  }

  if (msgEl) {
    container.appendChild(msgEl);
  }

  if (wasNearBottom) {
    scrollToBottom();
  } else {
    const existingBtn = document.getElementById("scroll-to-bottom");
    if (!existingBtn) {
      document.body.appendChild(createScrollButton());
    }
  }
}
