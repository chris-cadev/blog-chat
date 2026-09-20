import { trackUmami } from "./umami";

const THEME_STORAGE_KEY = "blog-theme-mode";
const THEME_COOKIE_NAME = "theme-mode";

export function initTheme() {
  const themeToggle = document.getElementById("theme-toggle") as HTMLElement | null;
  const html = document.documentElement;

  function getStoredTheme(): string {
    try {
      const ls = localStorage.getItem(THEME_STORAGE_KEY);
      if (ls === "dark" || ls === "light") return ls;
    } catch {}
    const cookie = getThemeFromCookie();
    if (cookie === "nord" || cookie === "nord-light") return cookie === "nord" ? "dark" : "light";
    if (cookie === "dark" || cookie === "light") return cookie;
    return "dark";
  }

  function applyTheme(mode: string) {
    const isDark = mode === "dark";
    html.setAttribute("data-theme-mode", isDark ? "dark" : "light");
    // compat for any legacy selectors
    html.setAttribute("data-theme", isDark ? "nord" : "nord-light");
    try {
      localStorage.setItem(THEME_STORAGE_KEY, isDark ? "dark" : "light");
    } catch {}
    setThemeCookie(isDark ? "nord" : "nord-light");
    if (themeToggle) {
      if (themeToggle instanceof HTMLInputElement) {
        themeToggle.checked = isDark;
      } else {
        themeToggle.textContent = isDark ? "☀️" : "🌙";
      }
    }
  }

  applyTheme(getStoredTheme());

  if (themeToggle) {
    if (themeToggle instanceof HTMLInputElement) {
      themeToggle.addEventListener("change", () => {
        const newMode = (themeToggle as HTMLInputElement).checked ? "dark" : "light";
        applyTheme(newMode);
        trackUmami("Theme Toggle", { theme: newMode });
      });
    } else {
      themeToggle.addEventListener("click", () => {
        const current = html.getAttribute("data-theme-mode") === "dark" ? "dark" : "light";
        const next = current === "dark" ? "light" : "dark";
        applyTheme(next);
        trackUmami("Theme Toggle", { theme: next });
      });
    }
  }

  initChatPanel();
}

function initChatPanel() {
  const chatPanel = document.getElementById("chat-panel");
  const chatToggle = document.getElementById("chat-toggle");
  const chatBackdrop = document.getElementById("chat-backdrop");
  if (!chatPanel || !chatToggle) return;

  function openChat() {
    chatPanel!.classList.add("open");
    chatBackdrop?.classList.add("open");
    chatToggle!.classList.add("active");
  }
  function closeChat() {
    chatPanel!.classList.remove("open");
    chatBackdrop?.classList.remove("open");
    chatToggle!.classList.remove("active");
  }

  chatToggle.addEventListener("click", () => {
    if (chatPanel.classList.contains("open")) closeChat();
    else openChat();
  });
  chatBackdrop?.addEventListener("click", closeChat);
}

function getThemeFromCookie(): string | null {
  const cookies = document.cookie.split(";");
  for (const cookie of cookies) {
    const [name, value] = cookie.trim().split("=");
    if (name === THEME_COOKIE_NAME) return value;
  }
  return null;
}

function setThemeCookie(theme: string) {
  const expires = new Date();
  expires.setFullYear(expires.getFullYear() + 1);
  document.cookie = `${THEME_COOKIE_NAME}=${theme};expires=${expires.toUTCString()};path=/`;
}
