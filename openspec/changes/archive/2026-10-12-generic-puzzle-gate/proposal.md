# Proposal

## Why

The usernames post (`kris7pivot-xentyo-ricexen-riceseed-historia-usernames`) opens with a public TL;DR for Ulises, but the owner wants a tiny playful gate: Ulises types the answer to a personal question to reveal it. The existing `audio-puzzle` already implements a client-side gate with forever persistence; it is hardcoded to one `id` and one numeric answer. Making it generic lets the TL;DR (and any future block) reuse the same behavior without duplicating code, and keeps the voice-note `<details>` untouched.

Why now: the TL;DR needs to ship as a reusable collapsible rather than ad-hoc HTML, and HCI demands clear affordance, immediate feedback, and forgiving input.

## What Changes

- Generalize `audio-puzzle.ts` into a reusable puzzle gate that supports N instances per page, text answers, comma-separated aliases, and case-insensitive/trimmed comparison (micro-interactivity only, no real security).
- Keep audio puzzle working via backward-compatible selector; load the generic chunk only when `[data-puzzle]` (or legacy `#audio-puzzle`) exists.
- Convert the TL;DR blockquote in `content/{en,es,fr}/kris7pivot-xentyo-ricexen-riceseed-historia-usernames.md` from always-visible to gated: question "what is the username of the NT's crew member that likes a lot Pokemon videogames?" expected answer `Endaa` (alias handling for `Endaa3132`/`3132` if needed) reveals the TL;DR content. Voice note `<details>` unchanged.
- Persist solved state in `localStorage` per puzzle identity (like `audioPuzzleSolved:…`), so a returning visitor does not retype. Gracefully degrade when storage is unavailable.
- Follow HCI: visible locked affordance, clear question, inline error + hint, Enter-to-submit, focus management, `aria-live` for messages, and no layout shift on unlock.

## Capabilities

### New Capabilities
- `content-puzzle`: Generic client-side puzzle gate for article content — gated reveal, persistence, multi-instance, forgiving text match, and accessible feedback. This is the durable behavior; the TL;DR usage is one instance.

### Modified Capabilities
- _None_ — no existing spec to modify (repo has no specs yet).

## Impact

- `src/blog_chat/features/posts/client/audio-puzzle.ts` → generalized `puzzle.ts` (or renamed entry); `src/blog_chat/features/posts/client/main.ts` loader widened to `[data-puzzle]`; `vite.config.js` entry renamed/aliased to `puzzle` (keep `audio-puzzle.js` alias if needed for cache).
- `content/en|es|fr/kris7pivot-xentyo-ricexen-riceseed-historia-usernames.md` — TL;DR block replaced by gated HTML; no parser change.
- No backend, DB, or API changes. No CSP change (uses existing `'nonce'` script loading). Pure progressive enhancement; content remains in HTML (view-source visible — intentional, not a security boundary).
