import "./main.css";
import { initIframeLoader } from "./iframe-loader";
/* Posts feature entry point */

function trackUmami(event: string, data?: Record<string, string | undefined>): void {
  try {
    window.trackUmami?.(event, data);
  } catch {
    /* ignore tracking failures; never break the page */
  }
}

initIframeLoader();

function bindLinkTracking() {
  document.addEventListener("click", (event) => {
    const target = event.target as HTMLElement;
    const postEl = target.closest("[data-track-post]");
    if (postEl) {
      trackUmami("Post Click", { slug: postEl.getAttribute("data-track-post") });
      return;
    }
    const tagEl = target.closest("[data-track-tag]");
    if (tagEl) {
      trackUmami("Tag Click", { tag: tagEl.getAttribute("data-track-tag") });
    }
  });
}

bindLinkTracking();
