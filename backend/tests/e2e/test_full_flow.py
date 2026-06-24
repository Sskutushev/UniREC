BRIEF_TEXT = (
    "We need a landing page for a B2B SaaS analytics product. "
    "The page should explain the product, include pricing teaser, "
    "capture emails, and be ready in 2 weeks. Budget is limited."
)


async def test_full_decode_flow(client) -> None:
    decode_response = await client.post("/v1/briefs/decode", json={"text": BRIEF_TEXT})

    assert decode_response.status_code == 200
    payload = decode_response.json()
    assert payload["status"] == "completed"

    run_response = await client.get(f"/v1/briefs/runs/{payload['run_id']}")
    assert run_response.status_code == 200
    assert run_response.json()["result"]["summary"]

    health_response = await client.get("/health")
    assert health_response.status_code == 200
