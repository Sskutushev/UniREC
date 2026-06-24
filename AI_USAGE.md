# AI Usage

## Tools Used

- Claude Code for repository scaffolding, backend implementation, extension implementation, and test authoring

## Delegated Areas

- scaffolding of the monorepo layout
- FastAPI service and provider structure
- Chrome Extension component skeletons and hook flow
- test case drafting for backend and extension
- CI workflow assembly

## Example Prompts

1. "Scaffold a monorepo for a FastAPI backend and WXT Chrome Extension with clean architecture boundaries."
2. "Implement a fake LLM provider with deterministic valid and failure modes for structured output tests."
3. "Build a popup UX for decoding briefs with loading, error, copy, and result states."
4. "Add backend tests for invalid provider output, provider failure, cache behavior, and API happy path."
5. "Create a chained CI pipeline for lint, format, typecheck, tests, and final build artifacts."

## What Was Accepted

- initial repository layout
- baseline domain schemas and repository patterns
- first-pass popup component structure

## What Was Changed Or Rewritten

- dependency wiring for cache and provider overrides in tests
- provider structured-output handling to store raw payloads safely
- popup styling and composition to make the extension more intentional and readable
- CI design from separate workflows into a single chained pipeline

## Verification Process

- backend: `ruff`, `ruff format --check`, `mypy`, `pytest`, `uv build`
- extension: `eslint`, `tsc --noEmit`, `vitest`, `wxt build`
- CI: workflow structure validated locally before push

## Agent Mistakes Or Limitations Found

- the first CI version used separate workflows instead of one chained pipeline
- the first health test setup only mocked Redis for dependency-injected routes, not cache-dependent service construction
- the first hook tests triggered React act warnings and needed cleanup
- the first extension WXT config missed `srcDir`, which broke the build
