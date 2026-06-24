import pytest

from app.api.dependencies import get_provider
from app.main import app
from app.providers.fake import FakeProvider

BRIEF_TEXT = (
    "We need a landing page for a B2B SaaS analytics product. "
    "The page should explain the product, include pricing teaser, "
    "capture emails, and be ready in 2 weeks. Budget is limited."
)


@pytest.mark.parametrize(
    ("mode", "expected_code"),
    [
        ("provider_error", "provider_failure"),
        ("invalid_json", "validation_error"),
        ("invalid_severity", "validation_error"),
        ("missing_fields", "validation_error"),
    ],
)
async def test_decode_failure_modes(client, mode: str, expected_code: str) -> None:
    app.dependency_overrides[get_provider] = lambda: FakeProvider(mode=mode)

    response = await client.post("/v1/briefs/decode", json={"text": BRIEF_TEXT})

    assert response.status_code == 502
    assert response.json()["error_code"] == expected_code
    app.dependency_overrides.pop(get_provider, None)


async def test_decode_rejects_short_input(client) -> None:
    response = await client.post("/v1/briefs/decode", json={"text": "too short"})

    assert response.status_code == 422
