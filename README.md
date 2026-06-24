# AI Brief Decoder Lite

Monorepo for the AnytoolAI test assignment: a FastAPI backend, a Chrome Extension frontend, and local tooling for reproducible development.

## Current Status

- Stage 0 scaffold is in place.
- Backend, extension, tests, and Docker layers are prepared as structured modules.
- Documentation lives in `docs/` and will be expanded alongside implementation.

## Repository Layout

- `backend/` — FastAPI service, domain, providers, repositories, tests, and migrations
- `extension/` — WXT + React Chrome Extension
- `docker/` — local compose stacks
- `docs/` — project documentation and delivery notes
- `.github/workflows/` — CI workflow definitions

## Workflow Rules

- Every roadmap step is implemented on a dedicated branch.
- Commits follow Conventional Commits in English.
- Local checks must pass before code is pushed.

## Next Milestone

Implement the backend domain, persistence, provider abstraction, and API slices.
