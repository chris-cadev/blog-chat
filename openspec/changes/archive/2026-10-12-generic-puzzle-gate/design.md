# Design

## Context

See `proposal.md` for why. Current state: `audio-puzzle.ts` is a single-instance IIFE bound to `#audio-puzzle` with hard-coded child ids (`puzzle-gate`, `puzzle-audio`, etc.), numeric `Number()` compare, and key `audioPuzzleSolved:${EXPECTED}`. It is split as a Vite entry (`audio-puzzle`) loaded lazily by `posts/client/main.ts:14` only if the element exists. The TL;DR for Ulises is a plain blockquote plus a separate voice `<details>` (to stay untouched). Constraints: no backend, no new deps, reuse existing tokens/CSP, keep progressive enhancement, follow HCI (visibility, feedback, affordance, forgiveness, consistency).

## Goals / Non-Goals

**Goals:**
- One generic chunk that gates any block (TL;DR + legacy audio) with same forever persistence.
- Authoring = paste a small HTML snippet in markdown; no parser or server change.
- HCI: clear question affordance, instant inline feedback, keyboard + screen-reader usable, forgiving input, no layout jump.

**Non-Goals:**
- Real security / obfuscation — answers stay in HTML (micro-interactivity only).
- Search/index hiding — content remains in source for crawlers/view-source.
- New markdown syntax or shortcode engine.
- Redesign of voice `<details>` or other article chrome.

## Decisions

**1. Generalize `audio-puzzle.ts` → `puzzle.ts` (keep backward compat)**
- Why: avoids duplication, keeps the "chunk only if needed" pattern the codebase already uses.
- How: change entry from `#audio-puzzle` to `querySelectorAll('[data-puzzle], #audio-puzzle')` loop. Each root owns its gate/content/input/btn/msg via scoped selectors (`.puzzle-gate`, `.puzzle-content`, etc.) instead of global ids, so N instances work. Derive `EXPECTED` as comma-split `data-expected` → normalized set (`trim().toLowerCase()`). Empty → no-op. Keep `STORAGE_KEY = puzzleSolved:${root.id || 'puzzle'}:${primaryExpected}` to stay per-page/per-puzzle and mirror audio behavior. On correct, `gate.hidden=true` / `content.hidden=false` (or `display`), `localStorage.setItem`, `trackUmami('Puzzle Solved', {id, expected})`. On wrong, `msg.textContent` + `aria-live`, `input.focus()`. Wrap storage in try/catch.
- Alt considered: separate `tldr-puzzle.ts` — rejected (duplicate logic, two chunks).

**2. Loader in `posts/client/main.ts` widens selector**
- Why: minimal diff, single lazy-load site. Replace `getElementById('audio-puzzle')` with `querySelector('[data-puzzle], #audio-puzzle')`. Script src becomes `/static/puzzle.js` (add `audio-puzzle.js` alias in vite output if cache paranoia). No change to CSP — same `nonce` script injection.
- Alt: auto-import in article template — rejected (loads on every page).

**3. Match semantics: forgiving text, keep numeric for legacy**
- Why: new question is textual ("Endaa"), audio is numeric (855). Normalize to lowercased trimmed set for all; for numeric-only sets, also accept `Number()` equality so `855` still passes with comma handling already in old code.
- HCI mapping: forgiveness (Principles: error tolerance) — trim, case-insensitive, alias list covers `Endaa`/`Endaa3132`/`3132`; Enter key + click both work; `aria-live="polite"` + focus retention prevents silent failure.

**4. Vite entry rename with alias**
- Why: entry `audio-puzzle` → `puzzle` is cleaner; emitting both `puzzle.js` and `audio-puzzle.js` (via `build.rollupOptions.output` alias or copy) avoids 404 for cached HTML referencing old chunk during deploy.
- Alt: keep old name — confusing for a generic gate.

**5. Markup contract for authors**
- Preferred snippet per language (en/es/fr): wrapper `<div id="tldr-ulises" data-puzzle data-expected="Endaa,Endaa3132,3132" data-puzzle-id="tldr-ulises">` with `.puzzle-gate` (question + input `type="text" autocomplete="off"`, button `type="button"`, `.puzzle-msg aria-live="polite"`) and `.puzzle-content hidden` (TL;DR blockquote). IDs are optional; class-based queries make multi-instance safe. Voice `<details>` stays as sibling, no interaction.
- Same contract can gate audio: wrap existing `#audio-puzzle` with `data-puzzle` or keep legacy id + add class wrappers.

**6. Styling — reuse tokens, no new file**
- Why: consistency HCI. Gate uses `var(--bg-surface)`, `var(--border-strong)`, `var(--accent)` like voice details. Inline or 6-line block in `main.css` for `.puzzle-gate`/`.puzzle-content`; reveal uses `hidden` attribute rather than `display:none` toggle for a11y.

**7. Persistence identity**
- Key = `puzzleSolved:${puzzleId}:${normalizedPrimary}` — stable across reloads, distinct per language page (path includes `id` + primary alias). Lowercasing avoids `Endaa` vs `endaa` split keys. Try/catch on read/write.

## Risks / Trade-offs

- **Answers in HTML → trivial bypass** → Accepted; by design micro-interactivity. Mitigation: document as non-security in spec/proposal; no hashing theatre.
- **localStorage key collision if author reuses id** → Mitigation: recommend unique `id` per puzzle + include primary expected in key; collisions just share solved flag.
- **Two script names during transition** → Mitigation: emit alias so old cached page still fetches `audio-puzzle.js`.
- **JS disabled → content stays hidden** → Mitigation: content is hidden via JS on enhance (or `hidden` added by JS, not server), but if server renders `hidden` + no JS, user loses TL;DR. Use progressive: server renders gate+content with gate visible and content `hidden`; `<noscript>` reveals TL;DR as fallback (small snippet).
- **i18n question text** → Mitigation: question lives in markup (translated per md), only `data-expected` is shared.

## Migration Plan

1. Add `puzzle.ts` and vite entry `puzzle` (alias `audio-puzzle.js`).
2. Update `posts/client/main.ts` selector/src.
3. Update `content/{en,es,fr}/kris7pivot…md` TL;DR to gated snippet (keep voice details).
4. `mise run build` → verify `static/puzzle.js` (and alias) emitted, old pages without `[data-puzzle]` load no extra chunk.
5. Deploy; no rollback data. Rollback = revert commit, content shows gated (JS) but build will still emit generic chunk — safe.

## Open Questions

- None blocking. Minor: whether to emit both `puzzle.js` and `audio-puzzle.js` filenames or just rename references — can decide at implementation without changing specs.
