# Architecture

## Overview

blog-chat is a real-time chat application with an integrated markdown-based blog. It uses a feature-based architecture where each major functionality (accounts, chat, posts) is organized as a self-contained module.

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Backend                      │
├──────────────┬──────────────┬───────────────────────────┤
│   Accounts   │     Chat     │         Posts             │
│   (auth)     │  (WebSocket) │    (markdown blog)        │
├──────────────┴──────────────┴───────────────────────────┤
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
└─────────────────────────────────────────────────────────┘
```

## Backend Components

### Core Module (`src/blog_chat/core/`)

- **config.py** - Environment configuration (DATABASE_URL, JWT_SECRET, CONTENT_DIR)
- **database.py** - SQLAlchemy async engine setup, session management
- **responses.py** - Jinja2 template rendering helpers
- **filters.py** - Custom Jinja2 filters (markdown, etc.)
- **base.py** - SQLAlchemy declarative base

### Features Module (`src/blog_chat/features/`)

Each feature is a self-contained module with its own routes, models, and services:

#### Accounts (`features/accounts/`)

- JWT token creation/validation
- User model and database operations
- Cookie-based authentication

#### Chat (`features/chat/`)

- WebSocket endpoint at `/ws/chat`
- ConnectionManager for broadcasting to rooms
- Message model with room, username, content, timestamp
- Markdown rendering for messages

#### Posts (`features/posts/`)

- Markdown file parsing from `content/` directory
- Static blog pages
- Custom markdown parser

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
created_at: DATETIME
```

### Messages Table

```
id: INTEGER PRIMARY KEY
room_slug: VARCHAR(100)
user_id: INTEGER FK -> users.id
username: VARCHAR(50)
content: TEXT
timestamp: DATETIME
ip_address: VARCHAR(45)
```

## Security

- JWT tokens stored in HTTP-only cookies
- Passwords not stored (username-based auth)
- CORS configured for localhost
- GZip compression for responses
- SQLAlchemy prevents SQL injection

## Environment Variables

| Variable     | Description                            | Required                 |
| ------------ | -------------------------------------- | ------------------------ |
| DATABASE_URL | SQLite or PostgreSQL connection string | Yes                      |
| JWT_SECRET   | Secret key for JWT signing             | Yes                      |
| CONTENT_DIR  | Path to markdown blog files            | Yes (default: "content") |
