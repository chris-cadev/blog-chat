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
// Puzzle separado en TS: no va dentro de posts.js — chunk aparte, se carga solo si existe #audio-puzzle
function loadAudioPuzzle() {
  if (!document.getElementById("audio-puzzle")) return;
  const s = document.createElement("script");
  s.src = "/static/audio-puzzle.js";
  s.async = true;
  document.head.appendChild(s);
}
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", loadAudioPuzzle);
} else {
  loadAudioPuzzle();
}

function initImageZoom() {
  const style = document.createElement("style");
  style.textContent = `
    .zoom-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.88);display:flex;align-items:center;justify-content:center;gap:16px;padding:16px;z-index:9999;cursor:zoom-out;flex-wrap:wrap;overflow:auto}
    .zoom-overlay img{max-width:min(90vw,800px);max-height:90vh;object-fit:contain;border-radius:8px;box-shadow:0 10px 40px rgba(0,0,0,0.6);background:#fff}
    .zoom-overlay figcaption{color:#eee;text-align:center;margin-top:8px;font-size:0.9em}
    .zoom-overlay figure{margin:0;flex:1 1 400px;max-width:700px;display:flex;flex-direction:column;align-items:center}
    @media(max-width:700px){.zoom-overlay{flex-direction:column}}
  `;
  document.head.appendChild(style);

  document.addEventListener("click", (e) => {
    const target = e.target as HTMLElement;
    // solo imágenes dentro del artículo (para comparar Antes/Después y cualquier otra)
    const img = target.closest(".article-body figure img") as HTMLImageElement | null;
    if (!img) return;
    // evitar navegar al link de archive.org
    e.preventDefault();
    const figure = img.closest("figure");
    const compareRoot = img.closest("#compare-images");
    const overlay = document.createElement("div");
    overlay.className = "zoom-overlay";
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-label", "Imagen ampliada, click para cerrar");

    const close = () => overlay.remove();
    overlay.addEventListener("click", close);
    const esc = (ev: KeyboardEvent) => {
      if (ev.key === "Escape") {
        close();
        document.removeEventListener("keydown", esc);
      }
    };
    document.addEventListener("keydown", esc);

    if (compareRoot) {
      // modo comparación: clona las dos figuras (Antes + Después) para comparar lado a lado
      const figures = compareRoot.querySelectorAll("figure");
      figures.forEach((fig) => {
        const clone = fig.cloneNode(true) as HTMLElement;
        // quitar estilos restrictivos y asegurar imagen visible
        clone.style.maxWidth = "none";
        clone.style.flex = "1 1 400px";
        // si es placeholder sin img, mantener texto
        overlay.appendChild(clone);
      });
    } else {
      // zoom simple de una sola imagen
      const clone = document.createElement("figure");
      const cImg = document.createElement("img");
      cImg.src = img.src;
      cImg.alt = img.alt;
      const cap = figure?.querySelector("figcaption")?.textContent || img.alt || "";
      clone.appendChild(cImg);
      if (cap) {
        const cCap = document.createElement("figcaption");
        cCap.textContent = cap;
        clone.appendChild(cCap);
      }
      overlay.appendChild(clone);
    }

    document.body.appendChild(overlay);
  });
}
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initImageZoom);
} else {
  initImageZoom();
}

function bindLinkTracking() {
  document.addEventListener("click", (event) => {
    const target = event.target as HTMLElement;
    const tagEl = target.closest("[data-track-tag]");
    if (tagEl) {
      trackUmami("Tag Click", { tag: tagEl.getAttribute("data-track-tag") });
      return;
    }
    const postEl = target.closest("[data-track-post]");
    if (postEl) {
      trackUmami("Post Click", { slug: postEl.getAttribute("data-track-post") });
    }
  });
}

bindLinkTracking();

function initCopyButtons() {
  document.querySelectorAll<HTMLElement>(".article-body pre").forEach((pre) => {
    const btn = document.createElement("button");
    btn.className = "copy-btn";
    btn.textContent = "Copy";
    btn.setAttribute("aria-label", "Copy code to clipboard");
    btn.addEventListener("click", async () => {
      const code = pre.querySelector("code") ?? pre;
      try {
        await navigator.clipboard.writeText(code.textContent ?? "");
        btn.textContent = "Copied!";
        btn.classList.add("copied");
        setTimeout(() => {
          btn.textContent = "Copy";
          btn.classList.remove("copied");
        }, 1500);
      } catch {
        btn.textContent = "Failed";
      }
    });
    pre.appendChild(btn);
  });
}
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initCopyButtons);
} else {
  initCopyButtons();
}
