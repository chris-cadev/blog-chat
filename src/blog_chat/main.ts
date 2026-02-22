import "./styles/main.css";
import "htmx.org";
import { initChat } from "./ws-handlers";
import { initTheme } from "./theme";

initChat();
initTheme();
