# Documentation

Welcome to the blog-chat documentation.

## Quick Links

- [Architecture Overview](architecture.md) - System design and component breakdown
- [TODO Details](todos.md) - Detailed breakdown of all project tasks
- [Setup Guide](setup.md) - How to run the project locally

## What is blog-chat?

A real-time chat application with an integrated markdown-based blog. Features include:

- Live WebSocket chat in topic-based rooms
- Markdown file-based blog system
- JWT-based authentication
- Embeddable chat widget (planned)

## Tech Stack

- **Backend:** FastAPI + SQLAlchemy async
- **Frontend:** Vanilla TypeScript + Vite + HTMX
- **Real-time:** WebSockets
- **Database:** SQLite (dev) / PostgreSQL (prod)

For more details, see [Architecture](architecture.md).
