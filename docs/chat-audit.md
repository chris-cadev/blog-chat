# Chat Audit

Audit of the message chat functionality covering security, usability, UX, and HCI.
Findings are labeled S (security), U (usability/UX), A (HCI/accessibility), and C (correctness).

## Status

- **Implemented:** S1, S2, S3, S4, S5, U1, U2, U3, U5, A1, A2, and timezone correctness fixes.
- **Implemented (found during remediation):** live-message attribution — broadcasts were
  rendered with `is_own=True` for every recipient, so all users saw every live message styled
  as their own. Broadcasts now render per-recipient via `ConnectionManager.broadcast(room, make_payload)`.
- **Deferred:** S6, S7, S8, S9, U4, U6, U8 (see below).

---

## Deferred Work

Items deferred from the initial remediation pass. Tracked here with context and
pointers to the relevant code.

### S6 — Cookies missing `secure` flag

**Severity:** Medium

**What:** Auth and preference cookies are set without the `Secure` attribute, so
they would be transmitted over plaintext HTTP if the site is ever reached that way.

**Where:**
- `src/blog_chat/features/accounts/routes.py` — `chat_token` cookie in `set_username` / `clear_username`
- `src/blog_chat/features/posts/routes.py` — `lang` cookie in `_with_lang_cookie`
- `src/blog_chat/features/chat/client/ws-handlers.ts` — `chat_timezone` cookie

**To do:**
- Add `secure=True` (and `httponly=True` where the value is not read by JS) to each cookie.
- Consider `SameSite=Strict` for `chat_token`.
- Verify behind the Cloudflare tunnel the request still terminates as HTTPS.

### S7 — Trivial username impersonation

**Severity:** Medium

**What:** `set_username` issues a valid token for any claimed username, even if
that username already belongs to another user. There is no proof of ownership, so
anyone can post as anyone else. The global unique constraint on `User.username`
does not prevent this because existing users are reused rather than rejected.

**Where:**
- `src/blog_chat/features/accounts/routes.py:35-43`
- `src/blog_chat/features/accounts/services.py` — `create_token` / `decode_token`

**To do:**
- Decide the desired identity model (anonymous guest vs. claimed name).
- Options: block re-claiming an active username, require a salted token for
  ownership proof, or auto-suffix duplicates (e.g. `name#1234`).

### S8 — Broken data model / IP privacy

**Severity:** Medium

**What:**
- `Message.user_id` is never populated when a message is created, so messages are
  not linked to their `User` row.
- Raw `ip_address` is stored in plaintext on both `Message` and `User`, which is a
  privacy (GDPR) concern and is unnecessary for anonymous chat.

**Where:**
- `src/blog_chat/features/chat/websocket.py:119-124` — `Message(...)` created without `user_id`
- `src/blog_chat/features/chat/models.py` — `ip_address` column
- `src/blog_chat/features/accounts/models.py` — `ip_address` column

**To do:**
- Resolve the claimed user from the token and set `Message.user_id`.
- Hash IPs (e.g. SHA-256 with a daily salt) or stop storing them.

### S9 — Minor security items

**Severity:** Low

**What:**
- CORS `allow_origins=["localhost"]` in `src/blog_chat/app.py` is malformed (no
  scheme/port) and irrelevant to WebSockets.
- JWT is a bare HS256 username+exp payload — no `iss`/`aud`/`jti`, no revocation.
- Room slugs come from the client and are unbounded; arbitrary room names grow
  `ConnectionManager` state and DB rows.
- Concurrent registration of the same new username can raise an unhandled
  `IntegrityError` (500).

**To do:**
- Tighten CORS origins.
- Add standard JWT claims and a revocation strategy if tokens ever gate privileged actions.
- Whitelist or normalize room slugs.
- Catch `IntegrityError` in `set_username`.

### U4 — No pagination for older messages

**Severity:** Low

**What:** Chat history is hard-limited to the 50 most recent messages
(`src/blog_chat/features/chat/websocket.py:76`). Older messages are unreachable.

**To do:**
- Add an HTTP or WS "load older" flow that returns messages before a cursor/ID.
- Render a "Load older messages" control at the top of the log.

### U6 — Inconsistent time rendering

**Severity:** Low

**What:** Server renders `humanize.naturaltime` strings ("2 minutes ago") while the
client re-renders with its own `formatRelativeTime` ("2m ago"). Future timestamps
produce odd negative values.

**Where:**
- `src/blog_chat/features/chat/routes.py` — `format_timestamp`
- `src/blog_chat/features/chat/client/ws-handlers.ts` — `formatRelativeTime`

**To do:**
- Pick one relative-time implementation and use it consistently.
- Handle future/clock-skew timestamps gracefully.

### U8 — Missing chat features

**Severity:** Low

**What:** No message edit/delete, typing indicator, unread states, or moderation
tooling. `docs/todos.md` lists replies, roles/permissions, and moderation as planned
work (PRD sections 4.2–4.4).

**To do:**
- Align with the roadmap in `docs/todos.md`.
