// audio-puzzle.ts — lógica separada solo para el blog con #audio-puzzle
// Entry aparte de Vite (no va dentro de posts.js/main.js). Se carga solo si existe el markup.
(() => {
  const root = document.getElementById("audio-puzzle") as HTMLElement | null;
  if (!root) return;
  const EXPECTED = (root.getAttribute("data-expected") || "855").trim();
  const STORAGE_KEY = `audioPuzzleSolved:${EXPECTED}`;
  const gate = document.getElementById("puzzle-gate") as HTMLElement | null;
  const audioWrap = document.getElementById("puzzle-audio") as HTMLElement | null;
  const input = document.getElementById("puzzle-input") as HTMLInputElement | null;
  const btn = document.getElementById("puzzle-btn") as HTMLButtonElement | null;
  const msg = document.getElementById("puzzle-msg") as HTMLElement | null;
  if (!gate || !audioWrap || !input || !btn || !msg) return;

  const unlock = (): void => {
    gate.style.display = "none";
    audioWrap.style.display = "block";
    msg.textContent = "";
  };

  const isSolved = (): boolean => {
    try {
      return localStorage.getItem(STORAGE_KEY) === EXPECTED;
    } catch {
      return false;
    }
  };

  if (isSolved()) {
    unlock();
    return;
  }

  const check = (): void => {
    const val = input.value.trim().replace(",", ".");
    const num = Number(val);
    const expectedNum = Number(EXPECTED);
    if (!Number.isNaN(num) && num === expectedNum) {
      try {
        localStorage.setItem(STORAGE_KEY, EXPECTED);
      } catch {}
      unlock();
      try {
        (window as unknown as { trackUmami?: (e: string, d?: Record<string, string>) => void }).trackUmami?.("Audio Puzzle Solved", { expected: EXPECTED });
      } catch {}
    } else {
      msg.textContent = "No es correcto. Pista: (2×84+3)×5. Intenta de nuevo.";
      msg.style.color = "var(--text-muted)";
      input.focus();
    }
  };

  btn.addEventListener("click", check);
  input.addEventListener("keydown", (e: KeyboardEvent) => {
    if (e.key === "Enter") check();
  });
})();
