"""Tests for X-Idempotency-Key deduplication on POST /v1/briefs/decode."""

BRIEF_TEXT = (
    "We need a landing page for a B2B SaaS analytics product. "
    "The page should explain the product, include pricing teaser, "
    "capture emails, and be ready in 2 weeks. Budget is limited."
)

IDEMPOTENCY_KEY = "test-idem-key-abc123"


async def test_idempotency_key_returns_same_run_on_retry(client) -> None:
    first = await client.post(
        "/v1/briefs/decode",
        json={"text": BRIEF_TEXT},
        headers={"X-Idempotency-Key": IDEMPOTENCY_KEY},
    )
    second = await client.post(
        "/v1/briefs/decode",
        json={"text": BRIEF_TEXT},
        headers={"X-Idempotency-Key": IDEMPOTENCY_KEY},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["run_id"] == second.json()["run_id"]


async def test_different_idempotency_keys_produce_different_runs(client) -> None:
    first = await client.post(
        "/v1/briefs/decode",
        json={"text": BRIEF_TEXT},
        headers={"X-Idempotency-Key": "key-alpha"},
    )
    second = await client.post(
        "/v1/briefs/decode",
        json={"text": BRIEF_TEXT},
        headers={"X-Idempotency-Key": "key-beta"},
    )

    assert first.json()["run_id"] != second.json()["run_id"]


async def test_request_without_idempotency_key_always_creates_new_run(client) -> None:
    first = await client.post("/v1/briefs/decode", json={"text": BRIEF_TEXT})
    second = await client.post("/v1/briefs/decode", json={"text": BRIEF_TEXT})

    assert first.json()["run_id"] != second.json()["run_id"]
