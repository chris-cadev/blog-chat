const THEME_COOKIE_NAME = "theme-mode";

export function initTheme() {
  const themeToggle = document.getElementById("theme-toggle") as HTMLInputElement | null;

  const savedTheme = getThemeFromCookie();
  if (savedTheme) {
    applyTheme(savedTheme);
    if (themeToggle) {
      themeToggle.checked = savedTheme === "nord";
    }
  } else {
    applyTheme("nord");
    if (themeToggle) {
      themeToggle.checked = true;
    }
  }

  if (themeToggle) {
    themeToggle.addEventListener("change", () => {
      const newTheme = themeToggle.checked ? "nord" : "nord-light";
      applyTheme(newTheme);
      setThemeCookie(newTheme);
    });
  }
}

function applyTheme(theme: string) {
  const html = document.documentElement;
  if (theme === "nord") {
    html.setAttribute("data-theme", "nord");
    html.setAttribute("data-theme-mode", "dark");
  } else {
    html.setAttribute("data-theme", "nord-light");
    html.setAttribute("data-theme-mode", "light");
  }
}

function getThemeFromCookie(): string | null {
  const cookies = document.cookie.split(";");
  for (const cookie of cookies) {
    const [name, value] = cookie.trim().split("=");
    if (name === THEME_COOKIE_NAME) {
      return value;
    }
  }
  return null;
}

function setThemeCookie(theme: string) {
  const expires = new Date();
  expires.setFullYear(expires.getFullYear() + 1);
  document.cookie = `${THEME_COOKIE_NAME}=${theme};expires=${expires.toUTCString()};path=/`;
}
