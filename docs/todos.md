# TODO Documentation

This file details each TODO item in the project, explaining what it is, why it matters, and where to start working on it.

---

## Embeddable Chat Widget

**Priority:** High

**What:** Create an embeddable version of the chat that can be inserted into external websites via iframe or JavaScript snippet.

**Why:** Allows the chat to be used on other blogs or websites, expanding reach.

**Where to start:**
- Create new route: `features/chat/routes.py` - add `/embed` endpoint
- New template: `features/chat/templates/embed.html`
- New client entry: `features/chat/client/embed.ts`
- May need standalone HTML without full page layout

**Related files:**
- `features/chat/routes.py` - existing WebSocket chat
- `features/chat/templates/` - existing chat templates

---

## Content File System Router

**Priority:** Medium

**What:** Add a left sidebar that displays the directory structure of the `content/` folder, allowing navigation through blog posts.

**Why:** Helps users discover content and understand the blog structure.

**Where to start:**
- Create directory listing service in `features/posts/services.py`
- Add sidebar component to base template
- Could use recursive traversal of `content/` directory

**Related files:**
- `features/posts/services.py` - existing post services
- `content/` - markdown files location

---

## Weather Indicator in Chat

**Priority:** Low

**What:** Show local weather information in chat messages or as part of user status.

**Why:** Adds personality and conversation starters to chat.

**Where to start:**
- Client-side: Get user location via browser Geolocation API
- Use free weather API (Open-Meteo recommended - no API key needed)
- Add to message metadata or user profile display

**Related files:**
- `features/chat/client/ws-handlers.ts` - WebSocket client
- `features/chat/routes.py` - message handling

---

## Move base.html to Core Module

**Priority:** Medium

**What:** Move the base HTML template from feature folders to the core module for shared use.

**Why:** DRY principle - avoid duplicating base template across features.

**Where to start:**
- Find existing `base.html` in feature templates
- Move to `core/templates/base.html`
- Update template inheritance in all templates

**Related files:**
- `core/responses.py` - template configuration

---

## Security Middleware for FastAPI

**Priority:** High

**What:** Add security headers (CSP, X-Frame-Options, etc.) using a middleware like `starlette-security` or custom middleware.

**Why:** Protect against common web vulnerabilities.

**Where to start:**
- Research available FastAPI security middleware
- Add to `app.py` after existing middleware
- Test with security headers scanner

**Related files:**
- `app.py` - FastAPI app setup

---

## Onboarding Chat Flow

**Priority:** High

**What:** 
1. Show prompt when user first arrives: "Choose Anonymous or enter username"
2. Prevent sending messages until one is selected

**Why:** Establish identity early, prevent spam, make chat more personal.

**Where to start:**
- Add onboarding UI in chat template
- Store choice in localStorage or cookie
- Block message send in `ws-handlers.ts` until username set
- Or: require username before WebSocket connection

**Related files:**
- `features/chat/client/ws-handlers.ts` - client-side chat logic
- `features/chat/templates/` - chat HTML templates
- `features/chat/routes.py` - WebSocket handler

---

## Create User on Valid Token

**Priority:** High

**What:** When a valid JWT token is presented, create a corresponding User record in the database (currently tokens store username but don't create DB user).

**Why:** Enables future features like user profiles, message history per user, etc.

**Where to start:**
- In `features/chat/routes.py` where token is validated
- Call user creation service after validating token
- Handle case where user already exists

**Related files:**
- `features/chat/routes.py` - `get_username_from_token` usage
- `features/accounts/services.py` - token handling
- `features/accounts/models.py` - User model

---

## Fix Cloudflare Tunnel Issue

**Priority:** Medium

**What:** Fix issues with Cloudflare tunnel (hosted tunnel service) not working properly.

**Why:** Needed for external access to the app.

**Where to start:**
- Check `.cloudflare/` directory for tunnel config
- Review Cloudflare tunnel logs
- Check hosted tunnel service documentation

**Related files:**
- `.cloudflare/` - tunnel configuration

---

## CI Script

**Priority:** Medium

**What:** Create automated CI script that:
1. Backs up database
2. Builds client assets (Vite)
3. Builds Docker container
4. Verifies requirements.txt is up to date

**Why:** Ensure consistent deployments and catch issues early.

**Where to start:**
- Create `scripts/ci.sh` or similar
- Use `pyproject.toml` or `requirements.txt` for dependency check
- Integrate with existing Dockerfile

**Related files:**
- `Dockerfile` - container build
- `vite.config.js` - frontend build
- `pyproject.toml` / `requirements.txt` - dependencies

---

## Group Near Messages (< 5 min)

**Priority:** Low

**What:** Visually group chat messages that are within 5 minutes of each other from the same user, showing only one username header.

**Why:** Cleaner chat UI, less visual clutter.

**Where to start:**
- Modify `render_message_template` in `routes.py`
- Pass "show_header" flag based on previous message timestamp
- Or: modify client-side rendering in `ws-handlers.ts`

**Related files:**
- `features/chat/routes.py` - `render_message_template` function
- `features/chat/client/ws-handlers.ts` - client rendering

---

## Docs Directory for Learning

**Priority:** Low

**What:** Create documentation in `docs/` explaining the topics and concepts learned while building this project.

**Why:** Share knowledge, future reference.

**Where to start:**
- Add markdown files to `docs/` folder
- Topics could include: FastAPI, WebSockets, SQLAlchemy async, HTMX

---

## Fix Negative Time Display Bug

**Priority:** Medium

**What:** Fix issue where human-readable time displays negative values (e.g., "5 minutes from now").

**Why:** Makes timestamps confusing/inaccurate.

**Where to start:**
- In `features/chat/routes.py` - `format_timestamp` function
- Check how `humanize.naturaltime` handles timestamps
- Add validation to ensure timestamp is in the past

**Related files:**
- `features/chat/routes.py` - `format_timestamp` function

---

## Fix Undefined on Send (Race Condition)

**Priority:** High

**What:** Fix race condition that causes "undefined" errors when sending messages.

**Why:** Causes errors and prevents message sending.

**Where to start:**
- Check `features/chat/client/ws-handlers.ts` for timing issues
- Ensure WebSocket is ready before sending
- Check message ID handling after send
- Look for async/await issues in client code

**Related files:**
- `features/chat/client/ws-handlers.ts` - client WebSocket handling
- `features/chat/routes.py` - server message handling
