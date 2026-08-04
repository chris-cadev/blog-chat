import "./main.css";
import "htmx.org";
import { initTheme } from "./theme";
import { initUmami, trackUmami } from "./umami";

initTheme();
initUmami();

function bindLanguageTracking() {
  document.addEventListener("click", (event) => {
    const el = (event.target as HTMLElement).closest("[data-track-language]");
    if (el) {
      trackUmami("Language Switch", { code: el.getAttribute("data-track-language") });
    }
  });
}

bindLanguageTracking();
