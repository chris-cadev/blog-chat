interface ChatMessage {
  id: number;
  username: string;
  content: string;
  timestamp: string;
}

function formatTimestamp(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function createMessageElement(data: ChatMessage): HTMLElement {
  const div = document.createElement("div");
  div.className = "chat chat-end";
  div.dataset.messageId = String(data.id);

  div.innerHTML = `
        <div class="chat-header flex items-center gap-2">
            <span class="font-bold text-sm">${data.username}</span>
            <span class="text-xs opacity-50">${formatTimestamp(data.timestamp)}</span>
        </div>
        <div class="chat-bubble chat-bubble-secondary">${data.content}</div>
    `;
  return div;
}

export function initChat(): void {
  const chatInput = document.getElementById("chat-input");
  const sendBtn = document.getElementById("send-btn");
  const chatMessages = document.getElementById("chat-messages");

  if (!chatInput || !sendBtn || !chatMessages) {
    console.error("Chat elements not found");
    return;
  }

  const chatInputEl = chatInput as HTMLInputElement;
  const sendBtnEl = sendBtn as HTMLButtonElement;
  const chatMessagesEl = chatMessages as HTMLElement;

  const room = document.body.getAttribute("data-room") || "offtopic";

  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/ws/chat?room=${room}`;
  const ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    console.log("WebSocket connected");
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === "history") {
      chatMessagesEl.innerHTML = "";
      data.messages.forEach((msg: ChatMessage) => {
        chatMessagesEl.appendChild(createMessageElement(msg));
      });
      chatMessagesEl.scrollTop = chatMessagesEl.scrollHeight;
    } else if (data.type === "message") {
      chatMessagesEl.appendChild(createMessageElement(data));
      chatMessagesEl.scrollTop = chatMessagesEl.scrollHeight;
    }
  };

  ws.onerror = (error) => {
    console.error("WebSocket error:", error);
  };

  ws.onclose = () => {
    console.log("WebSocket disconnected");
  };

  function sendMessage(): void {
    const message = chatInputEl.value.trim();
    if (message && ws.readyState === WebSocket.OPEN) {
      ws.send(message);
      chatInputEl.value = "";
    }
  }

  sendBtnEl.addEventListener("click", sendMessage);
  chatInputEl.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      sendMessage();
    }
  });
}
