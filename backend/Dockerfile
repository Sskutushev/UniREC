FROM python:3.12-slim

ARG INSTALL_DEV=false

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY . .

RUN if [ "$INSTALL_DEV" = "true" ]; then uv sync --frozen --extra dev; else uv sync --frozen --no-dev; fi

CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"]
