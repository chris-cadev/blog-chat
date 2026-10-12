# Tasks

## 1. Generic puzzle gate (replaces audio-puzzle as reusable)

- [x] 1.1 Create `src/blog_chat/features/posts/client/puzzle.ts` generalizing `audio-puzzle.ts` to handle `querySelectorAll('[data-puzzle], #audio-puzzle')`, per-root scoped gate/content/input/btn/msg, comma-separated `data-expected` with `trim().toLowerCase()` aliases, Enter+click, `aria-live` error, `localStorage` per `puzzleSolved:${id}:${primary}` with try/catch, and `hidden` toggle — verify file exists and builds via Vite
- [x] 1.2 Update Vite entry in `vite.config.js` to `puzzle` (emit `puzzle.js`, keep `audio-puzzle.js` alias/copy for backward compat) and widen loader in `src/blog_chat/features/posts/client/main.ts` to `[data-puzzle], #audio-puzzle` with `src=/static/puzzle.js` — verify `mise run build` outputs `static/puzzle.js` (and alias) and pages without puzzle fetch no extra chunk
- [x] 1.3 Keep legacy audio flow working through new chunk (numeric `855` still accepted, `audio-puzzle.html` markup without changes still solves and persists) — verify manually on a page with `#audio-puzzle` that solving persists across reload

## 2. TL;DR gated collapsible + HCI

- [x] 2.1 Replace TL;DR blockquote in `content/en/kris7pivot-xentyo-ricexen-riceseed-historia-usernames.md` with gated `[data-puzzle]` markup: question "what is the username of the NT's crew member that likes a lot Pokemon videogames?" `data-expected="Endaa,Endaa3132,3132"`, gate with `🔒` affordance, input `type=text`, unlock button, `.puzzle-msg aria-live=polite`, and hidden `.puzzle-content` holding the TL;DR — verify HTML renders in dev and localStorage persistence works case-insensitively
- [x] 2.2 Mirror the gated TL;DR markup in `content/es/...` and `content/fr/...` with translated question/summary (passwords unchanged) and leave voice `<details>` untouched — verify all three langs show gate and reveal correctly
- [x] 2.3 Add/HCI polish: focus stays in input on error, Enter submits, gate uses `var(--bg-surface)`/`var(--border-strong)` tokens like voice details, no layout shift on reveal, `noscript` fallback reveals TL;DR when JS off, keyboard operable — verify with keyboard-only nav and VoiceOver/NVDA `aria-live` announcement

## 3. Verification

- [x] 3.1 Build and smoke test: `mise run build` passes, `mise run test` unchanged, open usernames post in en/es/fr, confirm gate hidden→revealed→reload-persisted, and pages without puzzle load no `puzzle.js`
- [x] 3.2 Content QA: run `mise run geo -- content/en/kris7pivot-xentyo-ricexen-riceseed-historia-usernames.md` type linter or visual check for heading/color contrast, ensure `noscript` shows TL;DR fallback
