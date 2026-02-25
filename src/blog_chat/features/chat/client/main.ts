import "./main.css";
import { initChat } from "./ws-handlers";

document.body.addEventListener("htmx:afterSwap", (e) => {
  const usernameSection = document.getElementById("username-section");
  if (!usernameSection) return;

  const hasForm = usernameSection.querySelector("form");
  if (!hasForm) {
    window.location.reload();
  }
});

initChat();
