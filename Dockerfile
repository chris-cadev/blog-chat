FROM oven/bun:1 AS frontend

WORKDIR /app

COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

COPY vite.config.js tsconfig.json ./
COPY src ./src
RUN bun run build

FROM python:3.12-slim AS prerender

WORKDIR /app

RUN pip install --no-cache-dir --break-system-packages "mermaidx>=0.9.5"

COPY content ./content
COPY scripts/prerender_mermaid.py ./scripts/
COPY --from=frontend /app/static ./static
RUN python scripts/prerender_mermaid.py

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

COPY . .
COPY --from=prerender /app/static ./static

ENV PYTHONPATH=/app/src

EXPOSE 9091

CMD ["sh", "-c", "alembic upgrade head && exec python -m uvicorn blog_chat.app:app --host 0.0.0.0 --port 9091"]
