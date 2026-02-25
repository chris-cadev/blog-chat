let ws: WebSocket | null = null;

export function initChat() {
  const room = document.body.getAttribute("data-room") || "offtopic";
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/ws/chat?room=${room}`;

  ws = new WebSocket(wsUrl);

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === "history") {
      const container = document.getElementById("chat-messages");
      if (container) {
        container.innerHTML = "";
        data.messages.forEach((msg: any) => addMessage(msg));
      }
    } else if (data.type === "message") {
      addMessage(data);
    }
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

function sendMessage(input: HTMLInputElement) {
  const text = input.value.trim();
  if (text && ws && ws.readyState === WebSocket.OPEN) {
    ws.send(text);
    input.value = "";
  }
}

function addMessage(msg: any) {
  const container = document.getElementById("chat-messages");
  if (!container) return;

  const currentUsername = container.getAttribute("data-username") || "";
  const isOwnMessage = msg.username === currentUsername;

  const div = document.createElement("div");
  div.className = isOwnMessage ? "chat chat-start" : "chat chat-end";

  const time = msg.timestamp
    ? new Date(msg.timestamp).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      })
    : "";

  div.innerHTML = `
        <div class="chat-header">
            ${escapeHtml(msg.username)}
            <time class="text-xs opacity-50">${time}</time>
        </div>
        <div class="chat-bubble ${isOwnMessage ? "chat-bubble-primary" : "chat-bubble-secondary"}">${escapeHtml(msg.content)}</div>
    `;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function escapeHtml(text: string): string {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}
