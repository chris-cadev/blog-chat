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

For a complete list of tasks and priorities, see [TODO Documentation](docs/todos.md).
