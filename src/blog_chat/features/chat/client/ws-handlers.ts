let ws: WebSocket | null = null;

export function initChat() {
  const room = document.body.getAttribute("data-room") || "offtopic";
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/ws/chat?room=${room}`;

  ws = new WebSocket(wsUrl);
  const handlers = {
    history: loadChatHistory,
    message: addMessage,
  };

  type HandlerType = keyof typeof handlers;

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    const handler = handlers[data.type as HandlerType];
    if (handler) handler(data);
  };

  const input = document.getElementById("chat-input") as HTMLInputElement;
  const sendBtn = document.getElementById("send-btn");

  if (input && sendBtn) {
    sendBtn.addEventListener("click", () => sendMessage(input));
    input.addEventListener("keypress", (e) => {
      if (e.key === "Enter") sendMessage(input);
    });
  }
}

function loadChatHistory(data: any) {
  const container = document.getElementById("chat-messages");
  if (container) {
    container.innerHTML = "";
    data.messages.forEach((msg: any) => addHistoryMessage(msg));
  }
}

function addHistoryMessage(msg: any) {
  const container = document.getElementById("chat-messages");
  if (!container) return;

  container.insertAdjacentHTML("beforeend", msg.html);
}

function sendMessage(input: HTMLInputElement) {
  const text = input.value.trim();
  if (text && ws && ws.readyState === WebSocket.OPEN) {
    ws.send(text);
    input.value = "";
  }
}

function addMessage(data: any) {
  const container = document.getElementById("chat-messages");
  if (!container) return;

  container.prepend(document.createRange().createContextualFragment(data.html));
}
