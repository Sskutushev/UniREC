# Architecture

The project follows a clean layered structure:

1. Chrome Extension UI
2. FastAPI API layer
3. Service layer
4. Repository and cache layer
5. Provider gateway

The goal is to keep product-specific logic configurable while preserving a stable platform core.
