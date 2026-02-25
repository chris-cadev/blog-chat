let ws: WebSocket | null = null;
export { ws };
const MAX_CHARS = 280;
let isSending = false;
let timezoneSent = false;

function getTimezone(): string {
  return Intl.DateTimeFormat().resolvedOptions().timeZone;
}

function setTimezoneCookie(tz: string) {
  const expires = new Date();
  expires.setFullYear(expires.getFullYear() + 1);
  document.cookie = `chat_timezone=${tz};expires=${expires.toUTCString()};path=/;SameSite=Lax`;
}

function formatRelativeTime(isoString: string): string {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);

  if (diffSec < 60) return `${diffSec}s ago`;
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHour < 24) return `${diffHour}h ago`;
  return `${diffDay}d ago`;
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

function showEmptyState(show: boolean) {
  const empty = document.getElementById("chat-empty");
  if (empty) {
    empty.classList.toggle("hidden", !show);
  }
}

function isAtBottom(): boolean {
  const container = document.getElementById("chat-messages");
  if (!container) return true;
  const threshold = 100;
  return (
    container.scrollHeight - container.scrollTop - container.clientHeight <=
    threshold
  );
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
  btn.id = "scroll-to-bottom";
  btn.className =
    "btn btn-sm btn-primary fixed bottom-24 right-8 z-50 shadow-lg";
  btn.innerHTML = "New messages";
  btn.addEventListener("click", () => {
    scrollToTop(true);
    btn.remove();
  });
  return btn;
}

export function initChat() {
  const room = document.body.getAttribute("data-room") || "offtopic";
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/ws/chat?room=${room}`;

  ws = new WebSocket(wsUrl);
  const handlers = {
    history: loadChatHistory,
    message: addMessage,
    error: handleError,
  };

  type HandlerType = keyof typeof handlers;

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === "error") {
      handleError(data);
      return;
    }

    const handler = handlers[data.type as HandlerType];
    if (handler) handler(data);
  };

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
}

function loadChatHistory(data: any) {
  const container = document.getElementById("chat-messages");
  if (container) {
    container.innerHTML = "";
    if (data.messages.length === 0) {
      showEmptyState(true);
    } else {
      showEmptyState(false);
      data.messages.forEach((msg: any) => addHistoryMessage(msg));
      if (isAtBottom()) {
        scrollToTop();
      }
    }
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
  if (!ws || ws.readyState !== WebSocket.OPEN) return;
  if (isSending) return;

  isSending = true;
  setLoadingState(true);

  let messageToSend = text;
  if (!timezoneSent) {
    const tz = getTimezone();
    if (tz) {
      messageToSend = `tz:${tz}|${text}`;
      setTimezoneCookie(tz);
    }
    timezoneSent = true;
  }

  ws.send(messageToSend);
  input.value = "";
  updateCharCount();
}

export function onMessageSent() {
  const input = document.getElementById("chat-input") as HTMLInputElement;
  setLoadingState(false);
  if (input) {
    input.value = "";
    updateCharCount();
    input.focus();
  }
}

export function onMessageError() {
  setLoadingState(false);
  const input = document.getElementById("chat-input") as HTMLInputElement;
  if (input) input.focus();
}

function handleError(data: any) {
  setLoadingState(false);
  const input = document.getElementById("chat-input") as HTMLInputElement;
  if (input) {
    input.value = data.message.split(".")[0] + ".";
    input.focus();
  }
}

function addMessage(data: any) {
  if (isSending) {
    isSending = false;
    setLoadingState(false);
    const input = document.getElementById("chat-input") as HTMLInputElement;
    if (input) input.focus();
  }

  const container = document.getElementById("chat-messages");
  if (!container) return;

  showEmptyState(false);
  const wasAtBottom = isAtBottom();

  const temp = document.createElement("div");
  temp.innerHTML = data.html;
  const msgEl = temp.firstElementChild;

  const timeEl = msgEl?.querySelector("time");
  if (timeEl && data.timestamp) {
    timeEl.setAttribute("datetime", data.timestamp);
  }

  container.prepend(msgEl!);

  if (wasAtBottom) {
    scrollToTop();
  } else {
    const existingBtn = document.getElementById("scroll-to-bottom");
    if (!existingBtn) {
      document.body.appendChild(createScrollButton());
    }
  }
}
