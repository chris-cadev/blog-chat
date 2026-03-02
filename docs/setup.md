# Setup Guide

## Prerequisites

- Python 3.12+
- Node.js & Bun (for frontend build)
- PostgreSQL (optional, for production)

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd blog-chat

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the project root:

```bash
# Copy from example
cp example.env .env

# Edit .env with your values
DATABASE_URL=sqlite+aiosqlite:///chat.db
JWT_SECRET=your-secret-key-here
```

For production with PostgreSQL:
```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
```

### 3. Content Directory

Ensure the `content/` directory exists with markdown files:

```bash
# Verify content directory exists
ls content/
```

### 4. Run Development Server

```bash
# Using PDM (recommended)
pdm start

# Or using FastAPI directly
fastapi dev src/blog_chat/app.py
```

The app will be available at `http://localhost:8000`

### 5. Frontend Development (Optional)

For live-reload frontend development:

```bash
# Using Bun (recommended)
bun run watch

# Or using Vite directly
npx vite
```

## Available Commands

| Command | Description |
|---------|-------------|
| `pdm start` | Run development server |
| `pdm prod` | Run production server on port 9091 |
| `pdm test` | Run tests with coverage |
| `pdm watch` | Watch mode for frontend |
| `bun run build` | Build frontend assets |

## Project Scripts (package.json)

```bash
# Build frontend
bun run build

# Watch mode
bun run watch
```

## Testing

```bash
# Run all tests
pdm test

# Or directly with pytest
pytest -v
```

## Building for Production

### 1. Build Frontend

```bash
bun run build
```

This outputs to `static/` directory.

### 2. Build Docker Container

```bash
docker build -t blog-chat .
docker run -p 9091:9091 blog-chat
```

### 3. Using Docker Compose

```bash
docker-compose up -d
```

## Database

### SQLite (Development)

Default database is `chat.db` (SQLite). Created automatically on first run.

### PostgreSQL (Production)

Set `DATABASE_URL` to PostgreSQL connection string:
```
postgresql+asyncpg://username:password@localhost/databasename
```

## Project Structure Reference

```
blog-chat/
├── src/blog_chat/           # Python source code
│   ├── app.py              # FastAPI application
│   ├── core/               # Core utilities
│   │   ├── config.py       # Configuration
│   │   ├── database.py     # Database setup
│   │   └── responses.py    # Template rendering
│   └── features/           # Feature modules
│       ├── accounts/       # Authentication
│       ├── chat/           # Real-time chat
│       └── posts/          # Blog posts
├── static/                  # Built frontend assets
├── content/                 # Markdown blog posts
├── docs/                    # Documentation
├── tests/                   # Test suite
├── vite.config.js          # Vite build config
└── pyproject.toml          # Python project config
```

## Troubleshooting

### Database Errors

If you see database errors:
1. Check `DATABASE_URL` is set correctly
2. Ensure the database file/directory is writable
3. Try deleting `chat.db` to recreate

### Import Errors

If you see import errors:
1. Ensure you're in the virtual environment
2. Run `pip install -r requirements.txt` again

### Frontend Not Loading

1. Run `bun run build` to generate static files
2. Check `static/` directory has files
3. Ensure `/static` mount point works in app

### WebSocket Connection Failed

1. Check browser console for errors
2. Ensure server is running
3. Verify WebSocket endpoint is accessible

## Development Workflow

1. Start backend: `pdm start`
2. Start frontend watch: `bun run watch` (optional)
3. Make changes to code
4. Run tests: `pdm test`
5. Build frontend: `bun run build` (before commit)
