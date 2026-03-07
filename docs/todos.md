# TODO Documentation

This file details each TODO item in the project, explaining what it is, why it matters, and where to start working on it.

> **Note:** Items are prioritized based on PRD alignment. Items without PRD reference are optional enhancements.

---

## HIGH PRIORITY (PRD Required)

### Topic Voting System

**Priority:** High (PRD Section 4.3)

**What:** Users can vote on topics. One vote per user per topic. Votes influence topic ordering on homepage.

**Where to start:**
- Create `features/voting/models.py` - Vote model (user_id, topic_id, created_at)
- Add voting endpoint in `features/voting/routes.py`
- Update topic list to sort by votes
- Frontend: Add vote button to topic cards

**Related files:**
- `features/posts/` - existing topic/posts
- `features/accounts/models.py` - User model

---

### User Roles & Permissions

**Priority:** High (PRD Section 4.4)

**What:** Implement role-based access control with roles: Admin, Moderator, Regular User, Guest.

**Where to start:**
- Add `role` field to User model
- Create permission decorator/dependency
- Add moderation UI (delete messages, warn users)
- Update templates to show role-appropriate controls

**Related files:**
- `features/accounts/models.py` - User model
- `features/chat/routes.py` - message handling

---

### Thread-Like Replies

**Priority:** High (PRD Section 4.2)

**What:** Allow replies to specific messages to maintain sub-discussions.

**Where to start:**
- Add `parent_id` to Message model
- Update message template to show reply button
- Create thread view component
- Add indentation/nesting in UI

**Related files:**
- `features/chat/` - existing chat module

---

### Anonymous Users

**Priority:** High (PRD Section 4.4)

**What:** Allow anonymous participation without registration.

**Where to start:**
- Allow WebSocket connections without authentication
- Generate random anonymous usernames
- Track anonymous users via session/cookie

**Related files:**
- `features/chat/routes.py` - WebSocket handler

---

### Create User on Valid Token

**Priority:** High (PRD Section 4.4)

**What:** When a valid JWT token is presented, create a corresponding User record in the database.

**Why:** Enables future features like user profiles, message history per user.

**Where to start:**
- In `features/chat/routes.py` where token is validated
- Call user creation service after validating token
- Handle case where user already exists

**Related files:**
- `features/chat/routes.py` - `get_username_from_token` usage
- `features/accounts/services.py` - token handling
- `features/accounts/models.py` - User model

---

### Onboarding Chat Flow

**Priority:** High (PRD Section 4.4)

**What:** 
1. Show prompt when user first arrives: "Choose Anonymous or enter username"
2. Prevent sending messages until one is selected

**Why:** Establish identity early, prevent spam.

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

### Fix Undefined on Send (Race Condition)

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

---

### Security Middleware for FastAPI

**Priority:** High (PRD Section 4 Non-Functional)

**What:** Add security headers (CSP, X-Frame-Options, etc.) using middleware.

**Why:** Protect against common web vulnerabilities. PRD requires GDPR-ready security.

**Where to start:**
- Research available FastAPI security middleware
- Add to `app.py` after existing middleware
- Test with security headers scanner

**Related files:**
- `app.py` - FastAPI app setup

---

## MEDIUM PRIORITY (PRD Required)

### Topic Sorting & Discovery

**Priority:** Medium (PRD Section 4.1)

**What:** Sort topics by newest, trending, or community votes.

**Where to start:**
- Add sort query parameter to topic list endpoint
- Implement sorting logic (by date, vote count)
- Update frontend to show sort options
- Add trending calculation

**Related files:**
- `features/posts/` - existing posts module

---

### Search Within Topics

**Priority:** Medium (PRD Section 4.5)

**What:** Search within a topic by keywords, user, or date.

**Where to start:**
- Add search endpoint in `features/chat/routes.py`
- Implement full-text search on messages
- Add search UI component

**Related files:**
- `features/chat/` - chat module

---

### Content File System Router

**Priority:** Medium (PRD Section 4.1)

**What:** Add a left sidebar that displays the directory structure of the `content/` folder.

**Why:** Helps users discover content and understand the blog structure.

**Where to start:**
- Create directory listing service in `features/posts/services.py`
- Add sidebar component to base template
- Could use recursive traversal of `content/` directory

**Related files:**
- `features/posts/services.py` - existing post services
- `content/` - markdown files location

---

### Move base.html to Core Module

**Priority:** Medium

**What:** Move the base HTML template from feature folders to the core module.

**Why:** DRY principle - avoid duplicating base template.

**Where to start:**
- Find existing `base.html` in feature templates
- Move to `core/templates/base.html`
- Update template inheritance in all templates

**Related files:**
- `core/responses.py` - template configuration

---

### Fix Negative Time Display Bug

**Priority:** Medium

**What:** Fix issue where human-readable time displays negative values.

**Why:** Makes timestamps confusing/inaccurate.

**Where to start:**
- In `features/chat/routes.py` - `format_timestamp` function
- Check how `humanize.naturaltime` handles timestamps
- Add validation to ensure timestamp is in the past

**Related files:**
- `features/chat/routes.py` - `format_timestamp` function

---

### CI Script

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

### Fix Cloudflare Tunnel Issue

**Priority:** Medium

**What:** Fix issues with Cloudflare tunnel not working properly.

**Why:** Needed for external access to the app.

**Where to start:**
- Check `.cloudflare/` directory for tunnel config
- Review Cloudflare tunnel logs
- Check hosted tunnel service documentation

**Related files:**
- `.cloudflare/` - tunnel configuration

---

## LOW PRIORITY (PRD Optional / Nice-to-Have)

### Embeddable Chat Widget

**Priority:** Low (PRD Section 4.7 - Future)

**What:** Create an embeddable version of the chat for external websites.

**Where to start:**
- Create new route: `features/chat/routes.py` - add `/embed` endpoint
- New template: `features/chat/templates/embed.html`
- New client entry: `features/chat/client/embed.ts`

**Related files:**
- `features/chat/routes.py` - existing WebSocket chat
- `features/chat/templates/` - existing chat templates

---

### Notifications System

**Priority:** Low (PRD Section 4.6 - Future)

**What:** Notify users of new replies to topics they follow.

**Where to start:**
- Create notification model
- Add notification service
- Implement WebSocket or polling for real-time notifications

**Related files:**
- `features/chat/` - existing chat module

---

### Group Near Messages (< 5 min)

**Priority:** Low

**What:** Visually group chat messages within 5 minutes from the same user.

**Why:** Cleaner chat UI, less visual clutter.

**Where to start:**
- Modify `render_message_template` in `routes.py`
- Pass "show_header" flag based on previous message timestamp
- Or: modify client-side rendering in `ws-handlers.ts`

**Related files:**
- `features/chat/routes.py` - `render_message_template` function
- `features/chat/client/ws-handlers.ts` - client rendering

---

### Weather Indicator in Chat

**Priority:** Low (Not in PRD)

**What:** Show local weather information in chat messages or as part of user status.

**Where to start:**
- Client-side: Get user location via browser Geolocation API
- Use free weather API (Open-Meteo - no API key needed)
- Add to message metadata or user profile display

**Related files:**
- `features/chat/client/ws-handlers.ts` - WebSocket client
- `features/chat/routes.py` - message handling

---

### Docs Directory for Learning

**Priority:** Low

**What:** Create documentation in `docs/` explaining topics learned while building.

**Where to start:**
- Add markdown files to `docs/` folder
- Topics could include: FastAPI, WebSockets, SQLAlchemy async, HTMX
