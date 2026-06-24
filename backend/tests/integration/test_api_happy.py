BRIEF_TEXT = (
    "We need a landing page for a B2B SaaS analytics product. "
    "The page should explain the product, include pricing teaser, "
    "capture emails, and be ready in 2 weeks. Budget is limited."
)


async def test_decode_happy_path(client) -> None:
    response = await client.post("/v1/briefs/decode", json={"text": BRIEF_TEXT})

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["result"]["summary"]
