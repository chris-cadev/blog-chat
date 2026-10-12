// puzzle.ts: generic gate for content blocks, backward compatible with #audio-puzzle
// Loaded only when [data-puzzle] or #audio-puzzle exists (see posts/client/main.ts)
(() => {
  const roots = document.querySelectorAll<HTMLElement>("[data-puzzle], #audio-puzzle");
  if (!roots.length) return;

  roots.forEach((root) => {
    const rawExpected = (root.getAttribute("data-expected") || "").trim();
    if (!rawExpected) return;
    const aliases = rawExpected
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
    if (!aliases.length) return;
    const normalizedAliases = aliases.map((s) => s.toLowerCase());
    const primary = normalizedAliases[0];
    const puzzleId = root.id || root.getAttribute("data-puzzle-id") || "puzzle";
    const storageKey = `puzzleSolved:${puzzleId}:${primary}`;
    // keep legacy audio key so previously solved users stay solved
    const legacyKey = `audioPuzzleSolved:${rawExpected.split(",")[0].trim()}`;

    // scoped elements: prefer class, fall back to legacy ids
    const gate =
      (root.querySelector<HTMLElement>(".puzzle-gate") as HTMLElement | null) ||
      (root.querySelector<HTMLElement>("#puzzle-gate") as HTMLElement | null);
    const content =
      (root.querySelector<HTMLElement>(".puzzle-content") as HTMLElement | null) ||
      (root.querySelector<HTMLElement>("#puzzle-audio") as HTMLElement | null) ||
      (root.querySelector<HTMLElement>("#puzzle-content") as HTMLElement | null);
    const input =
      (root.querySelector<HTMLInputElement>(".puzzle-input") as HTMLInputElement | null) ||
      (root.querySelector<HTMLInputElement>("#puzzle-input") as HTMLInputElement | null);
    const btn =
      (root.querySelector<HTMLButtonElement>(".puzzle-btn") as HTMLButtonElement | null) ||
      (root.querySelector<HTMLButtonElement>("#puzzle-btn") as HTMLButtonElement | null);
    const msg =
      (root.querySelector<HTMLElement>(".puzzle-msg") as HTMLElement | null) ||
      (root.querySelector<HTMLElement>("#puzzle-msg") as HTMLElement | null);
    if (!gate || !content || !input || !btn || !msg) return;

    // ensure a11y live region
    if (!msg.hasAttribute("aria-live")) msg.setAttribute("aria-live", "polite");

    const unlock = (): void => {
      gate.hidden = true;
      gate.style.display = "none";
      content.hidden = false;
      content.style.display = "block";
      msg.textContent = "";
      // move focus to revealed content for reading order
      try {
        content.setAttribute("tabindex", "-1");
        (content as HTMLElement).focus({ preventScroll: true });
      } catch {}
    };

    const isSolved = (): boolean => {
      try {
        if (localStorage.getItem(storageKey) === primary) return true;
        // legacy audio check
        if (legacyKey && localStorage.getItem(legacyKey) === rawExpected.split(",")[0].trim()) return true;
        // also accept new key stored as "1" from older generic impl
        if (localStorage.getItem(storageKey)) return localStorage.getItem(storageKey) === primary;
      } catch {
        return false;
      }
      return false;
    };

    if (isSolved()) {
      unlock();
      return;
    }

    // progressive enhance: hide content until JS confirms not solved (keeps noscript visible)
    // if content was not already hidden by HTML, hide it now
    if (!content.hidden && content.style.display !== "none") {
      // only hide if not already solved, keep gate visible
      content.hidden = true;
      content.style.display = "none";
    }

    const check = (): void => {
      const rawVal = input.value.trim();
      // numeric fallback for legacy 855: replace comma decimal
      const normalizedInput = rawVal.toLowerCase();
      const numericInput = rawVal.replace(",", ".");
      const numericAliases = aliases.map((a) => a.replace(",", "."));
      let ok = normalizedAliases.includes(normalizedInput);
      if (!ok) {
        // numeric equality check (audio puzzle)
        const num = Number(numericInput);
        if (!Number.isNaN(num)) {
          for (const a of numericAliases) {
            const expNum = Number(a);
            if (!Number.isNaN(expNum) && num === expNum) {
              ok = true;
              break;
            }
          }
        }
      }
      if (ok) {
        try {
          localStorage.setItem(storageKey, primary);
        } catch {}
        unlock();
        try {
          (window as unknown as { trackUmami?: (e: string, d?: Record<string, string>) => void }).trackUmami?.("Puzzle Solved", {
            id: puzzleId,
            expected: primary,
          });
          // keep legacy audio event for dashboards
          if (puzzleId === "audio-puzzle" || root.id === "audio-puzzle") {
            (window as unknown as { trackUmami?: (e: string, d?: Record<string, string>) => void }).trackUmami?.("Audio Puzzle Solved", {
              expected: rawExpected,
            });
          }
        } catch {}
      } else {
        msg.textContent = "Not quite. Try again.";
        // allow per-puzzle hint via data-hint
        const hint = root.getAttribute("data-hint");
        if (hint) msg.textContent += ` Hint: ${hint}`;
        msg.style.color = "var(--text-muted)";
        input.focus();
      }
    };

    btn.addEventListener("click", check);
    input.addEventListener("keydown", (e: KeyboardEvent) => {
      if (e.key === "Enter") check();
    });
  });
})();
