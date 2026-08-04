# Project Commands

Run these through mise (e.g. `mise run test`):

- `mise run test` — run the test suite with coverage (`pytest -v --cov=blog_chat ...`)
- `mise run build` — build frontend assets into `static/` (`bun run build`)
- `mise run migrate` — apply pending DB migrations (uses `DATABASE_URL` from `.env`)
- `mise run dev` — run the dev server with hot reload (starts tmux session)
- `mise run deploy` — build frontend, migrate DB, then start the Docker Compose stack
