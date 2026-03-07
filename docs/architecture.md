# Architecture

## Overview

blog-chat is a real-time chat application with an integrated markdown-based blog. It uses a feature-based architecture where each major functionality (accounts, chat, posts) is organized as a self-contained module.

This document describes the current implementation. For planned features aligned with the PRD, see [TODO Details](todos.md).

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Backend                      │
├──────────────┬──────────────┬──────────────┬─────────────┤
│   Accounts   │     Chat     │    Posts     │   Voting    │
│   (auth)     │  (WebSocket) │ (markdown)  │  (planned)  │
├──────────────┴──────────────┴──────────────┴─────────────┤
│              SQLAlchemy Async ORM                       │
│              (SQLite / PostgreSQL)                      │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  Vite + TypeScript                      │
│    main.ts  │  chat.ts  │  posts.ts                     │
├─────────────────────────────────────────────────────────┤
│              HTMX for HTML-based interactivity          │
│              DaisyUI (planned)                          │
└─────────────────────────────────────────────────────────┘
```

## Backend Components

### Core Module (`src/blog_chat/core/`)

- **config.py** - Environment configuration (DATABASE_URL, JWT_SECRET, CONTENT_DIR)
- **database.py** - SQLAlchemy async engine setup, session management
- **responses.py** - Jinja2 template rendering helpers
- **filters.py** - Custom Jinja2 filters (markdown, etc.)
- **base.py** - SQLAlchemy declarative base
- **html.py** - HTML utilities

### Features Module (`src/blog_chat/features/`)

Each feature is a self-contained module with its own routes, models, and services:

#### Accounts (`features/accounts/`)

- JWT token creation/validation
- User model and database operations
- Cookie-based authentication
- **Planned:** Role-based access (Admin, Moderator, User, Guest)
- **Planned:** OAuth integration

#### Chat (`features/chat/`)

- WebSocket endpoint at `/ws/chat`
- ConnectionManager for broadcasting to rooms
- Message model with room, username, content, timestamp
- Markdown rendering for messages
- **Planned:** Thread replies (parent_id)
- **Planned:** Anonymous user support

#### Posts (`features/posts/`)

- Markdown file parsing from `content/` directory
- Static blog pages
- Custom markdown parser
- **Planned:** Topic voting integration

#### Voting (`features/voting/`)

- **Planned:** Vote model (topic_id, user_id, created_at)
- **Planned:** Vote endpoints
- **Planned:** Trending calculation

## Frontend Architecture

### Build System (Vite)

Entry points defined in `vite.config.js`:

- `core/client/main.ts` - Theme initialization, HTMX setup
- `features/chat/client/main.ts` - WebSocket chat client
- `features/posts/client/main.ts` - Blog post rendering

Output goes to `static/` directory.

### HTMX Integration

The frontend uses HTMX for server-side rendered interactivity without writing JavaScript for UI updates. This means:

- HTML responses from FastAPI include `hx-*` attributes
- HTMX handles AJAX requests and DOM swapping
- Reduces client-side JavaScript complexity

### UI Components

- **Current:** Vanilla CSS / custom styles
- **Planned:** DaisyUI for consistent, responsive design (see PRD Section 6)

### WebSocket Chat Client

Located in `features/chat/client/ws-handlers.ts`:

- Connects to `/ws/chat?room=<room_name>`
- Handles message history on connect
- Sends/receives JSON messages
- Renders HTML templates from server

## Data Flow

### Chat Message Flow

1. User types message in chat input
2. JavaScript sends message via WebSocket
3. Server receives message, stores in database
4. Server renders HTML template for message
5. Server broadcasts to all clients in room
6. Each client inserts HTML into DOM

### Blog Post Flow

1. Request to `/posts/<slug>` or `/blog/<slug>`
2. Router finds matching markdown file in `content/`
3. Parser converts markdown to HTML
4. Template renders with layout
5. HTML returned to browser

## Database Schema

### Users Table

```
id: INTEGER PRIMARY KEY
username: VARCHAR(50) UNIQUE
role: VARCHAR(20) DEFAULT 'user'  -- planned: admin, moderator, user, guest
ip_address: VARCHAR(45)
created_at: DATETIME
```

### Messages Table

```
id: INTEGER PRIMARY KEY
room_slug: VARCHAR(100)
user_id: INTEGER FK -> users.id  -- nullable for anonymous
username: VARCHAR(50)
content: TEXT
parent_id: INTEGER FK -> messages.id  -- planned: for thread replies
timestamp: DATETIME
ip_address: VARCHAR(45)
```

### Votes Table (Planned)

```
id: INTEGER PRIMARY KEY
topic_slug: VARCHAR(100)  -- references post/topic
user_id: INTEGER FK -> users.id  -- nullable for anonymous votes
created_at: DATETIME
```

## Security

- JWT tokens stored in HTTP-only cookies
- Passwords not stored (username-based auth)
- CORS configured for localhost
- GZip compression for responses
- SQLAlchemy prevents SQL injection
- **Planned:** Security middleware (CSP, X-Frame-Options)
- **Planned:** Rate limiting
- **Planned:** GDPR-ready data handling

## Environment Variables

| Variable     | Description                            | Required                 |
| ------------ | -------------------------------------- | ------------------------ |
| DATABASE_URL | SQLite or PostgreSQL connection string | Yes                      |
| JWT_SECRET   | Secret key for JWT signing             | Yes                      |
| CONTENT_DIR  | Path to markdown blog files            | Yes (default: "content") |

## PRD Alignment

This implementation follows the PRD with the following alignment:

| PRD Section | Status |
|-------------|--------|
| 4.1 Topic List / Blog Layer | ✅ Implemented |
| 4.2 Live Topic Chat | ✅ Implemented |
| 4.2 Thread-like replies | 🔲 Planned |
| 4.3 Topic Voting | 🔲 Planned |
| 4.4 User Authentication | ⚠️ Partial (JWT, no OAuth) |
| 4.4 User Roles | 🔲 Planned |
| 4.5 Persistent Chat History | ✅ Implemented |
| 4.6 Notifications | 🔲 Planned |
| 4.7 Optional Features | 🔲 Various |
| Non-functional: DaisyUI | 🔲 Planned |
| Non-functional: Security Headers | 🔲 Planned |

See [TODO Details](todos.md) for implementation priorities.
