# blog-chat

A real-time chat application with a built-in blog. Users can read markdown-based blog posts and chat together in topic-based rooms.

## TL;DR

**What it does:** A website where you can read blog articles and chat with other visitors in real-time. Think of it like a blog that has a live chat room attached - you can discuss posts as you read them.

**Who it's for:** Personal bloggers who want to build a community around their content, or anyone wanting a simple blog with live discussion.

## Tech Stack

- **Backend:** FastAPI (Python async web framework)
- **Database:** SQLAlchemy (async ORM) - supports SQLite for dev, PostgreSQL for production
- **Frontend:** Vanilla TypeScript + Vite build system + HTMX for interactivity
- **Real-time:** WebSockets for live chat
- **Auth:** JWT tokens (simple cookie-based authentication)
- **Content:** Markdown files as blog posts

## Project Structure

```
src/blog_chat/
├── app.py              # FastAPI application entry point
├── core/               # Shared utilities
│   ├── config.py       # Configuration (env vars, paths)
│   ├── database.py     # SQLAlchemy setup
│   ├── responses.py    # Template rendering
│   └── filters.py      # Jinja2 custom filters
├── features/
│   ├── accounts/       # User authentication
│   ├── chat/           # Real-time WebSocket chat
│   └── posts/          # Blog post system
└── client/             # Frontend TypeScript
```

---

## TODO

### Chat Features

- [ ] **Embeddable chat widget** - Make chat available as an embeddable iframe/JS widget for external sites
- [ ] **Group near messages** - Group chat messages within 5 minutes of each other visually
- [ ] **Weather indicator** - Show weather info in chat messages (e.g., user's local weather)

### Blog/Content Features

- [ ] **Content file system router** - Left sidebar showing blog content directory structure with navigation
- [ ] **Docs directory** - Write learning docs about topics understood in the project

### User Experience

- [ ] **Onboarding chat flow**
  - Prompt user to choose "Anonymous" or enter a username
  - Block message sending until username is set
- [ ] **Fix time display bug** - Human-readable time should always be positive (handle future timestamps correctly)
- [ ] **Fix undefined on send** - Race condition when sending messages causes undefined errors

### Infrastructure & Security

- [ ] **Move base.html to core module** - Consolidate shared templates
- [ ] **Security middleware** - Research and add appropriate security headers for FastAPI
- [ ] **Fix Cloudflare tunnel** - Resolve hosted tunnel service issues
- [ ] **CI Script**
  - Backup database
  - Build client assets
  - Build container
  - Verify requirements.txt

### User Management

- [ ] **Create user on valid token** - Create database user record when a valid JWT token is presented (currently only stores username in token)
