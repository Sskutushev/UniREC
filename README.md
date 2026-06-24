# AI Brief Decoder Lite

AI Brief Decoder Lite is a local-first prototype for decoding raw client briefs into structured delivery output through a FastAPI backend and a Chrome Extension UI.

## What Is Included

- FastAPI service with `POST /v1/briefs/decode`, `GET /v1/briefs/runs/{run_id}`, and `GET /health`
- provider abstraction with deterministic fake provider and optional OpenAI provider via PydanticAI
- structured validation with Pydantic v2
- persisted decode runs through SQLAlchemy + Alembic models
- Redis-backed cache with graceful degradation
- WXT + React Chrome Extension popup for brief input, loading, results, copy actions, and errors
- local checks for lint, format, typecheck, tests, and final build artifacts
- chained GitHub Actions CI pipeline

## Architecture

Request flow:

1. The extension sends raw brief text to the backend.
2. The service layer selects a provider through the provider gateway.
3. Raw provider output is parsed and validated into `BriefResult`.
4. Runs are stored in the database and cache.
5. The extension renders the normalized result.

## Repository Layout

- `backend/` — FastAPI service, domain, providers, repositories, tests, and migrations
- `extension/` — WXT + React Chrome Extension
- `docker/` — local compose stacks
- `docs/` — project documentation and delivery notes
- `.github/workflows/` — CI workflow definitions

## Requirements

- Python `3.12`
- Node `22`
- `pnpm`
- Docker Desktop for local stack verification

## Quick Start

### 1. Backend setup

```bash
cd backend
uv sync --extra dev
```

### 2. Extension setup

```bash
pnpm install
```

### 3. Run local infrastructure

```bash
docker compose -f docker/docker-compose.yml up -d postgres redis
```

This exposes PostgreSQL on `localhost:5433` and Redis on `localhost:6380`.

### 4. Run the backend locally

```bash
cd backend
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/ai_brief_decoder REDIS_URL=redis://localhost:6380/0 PROVIDER=fake uv run alembic upgrade head
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/ai_brief_decoder REDIS_URL=redis://localhost:6380/0 PROVIDER=fake uv run uvicorn app.main:app --reload
```

Docs will be available at `http://localhost:8000/docs`.

### 5. Build the extension

```bash
cd extension
pnpm build
```

Load `extension/.output/chrome-mv3` into Chrome in Developer Mode.

## Local Checks

Backend:

```bash
cd backend
uv run ruff check .
uv run ruff format --check .
uv run mypy app
uv run pytest -q
uv build
```

Extension:

```bash
cd extension
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

## Provider Modes

Fake provider modes:

- `valid`
- `provider_error`
- `invalid_json`
- `invalid_severity`
- `missing_fields`

Set them through `FAKE_PROVIDER_MODE`.

For OpenAI, switch `PROVIDER=openai` and provide `OPENAI_API_KEY` in the environment.

## Docker Commands

Build the local stack:

```bash
docker compose -f docker/docker-compose.yml build
```

Run backend + infra:

```bash
docker compose -f docker/docker-compose.yml up -d postgres redis backend
```

Build extension artifact via Docker:

```bash
docker compose -f docker/docker-compose.yml up extension-builder
```

Run backend test stack:

```bash
docker compose -f docker/docker-compose.test.yml run --rm backend-tests
```

## CI Pipeline

- `Backend Quality`
- `Extension Quality`
- `E2E Quality`
- `Final Build`

Each job is chained with `needs`, so the final build only runs after lint, format, typecheck, tests, and e2e checks pass.

## Assumptions And Tradeoffs

- The decode flow is synchronous right now, but the run model and polling-friendly API shape allow async queue migration later.
- The fake provider is the default so the project works locally without paid API keys.
- E2E coverage is API-level in this prototype to keep the assignment local and reproducible.
