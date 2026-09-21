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

function syncLangSwitcher() {
  const search = window.location.search;
  document.querySelectorAll<HTMLElement>("[data-track-language]").forEach((el) => {
    const a = el.closest("a");
    if (a) {
      const url = new URL(a.href);
      url.search = search;
      a.href = url.href;
    }
  });
}

document.addEventListener("DOMContentLoaded", syncLangSwitcher);
document.body.addEventListener("htmx:afterSwap", syncLangSwitcher);
window.addEventListener("popstate", syncLangSwitcher);
