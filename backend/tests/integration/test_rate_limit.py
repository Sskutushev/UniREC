"""Tests for per-IP rate limiting on POST /v1/briefs/decode."""

from app.api.dependencies import get_runtime_settings
from app.core.config import Settings
from app.main import app

BRIEF_TEXT = (
    "We need a landing page for a B2B SaaS analytics product. "
    "The page should explain the product, include pricing teaser, "
    "capture emails, and be ready in 2 weeks. Budget is limited."
)


async def test_requests_within_limit_succeed(client) -> None:
    response = await client.post("/v1/briefs/decode", json={"text": BRIEF_TEXT})

    assert response.status_code == 200


async def test_requests_exceeding_limit_return_429(client) -> None:
    tight_settings = Settings(RATE_LIMIT_PER_MINUTE=2)
    app.dependency_overrides[get_runtime_settings] = lambda: tight_settings
    try:
        for _ in range(2):
            r = await client.post("/v1/briefs/decode", json={"text": BRIEF_TEXT})
            assert r.status_code == 200

        blocked = await client.post("/v1/briefs/decode", json={"text": BRIEF_TEXT})
        assert blocked.status_code == 429
        assert blocked.json()["detail"]["error_code"] == "rate_limit_exceeded"
    finally:
        app.dependency_overrides.pop(get_runtime_settings, None)
