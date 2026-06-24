BRIEF_TEXT = (
    "We need a landing page for a B2B SaaS analytics product. "
    "The page should explain the product, include pricing teaser, "
    "capture emails, and be ready in 2 weeks. Budget is limited."
)

CHROME_EXT_ORIGIN = "chrome-extension://abcdefghijklmnopqrstuvwxyzabcdef"


async def test_decode_happy_path(client) -> None:
    response = await client.post("/v1/briefs/decode", json={"text": BRIEF_TEXT})

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["result"]["summary"]


async def test_decode_result_contains_all_required_fields(client) -> None:
    response = await client.post("/v1/briefs/decode", json={"text": BRIEF_TEXT})
    result = response.json()["result"]

    required_fields = (
        "summary",
        "goals",
        "deliverables",
        "constraints",
        "risks",
        "clarifying_questions",
        "recommended_next_action",
    )
    for field in required_fields:
        assert field in result, f"missing field: {field}"

    assert isinstance(result["goals"], list)
    assert isinstance(result["risks"], list)
    for risk in result["risks"]:
        assert risk["severity"] in ("low", "medium", "high")


async def test_cors_allows_chrome_extension_origin(client) -> None:
    response = await client.options(
        "/v1/briefs/decode",
        headers={
            "Origin": CHROME_EXT_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == CHROME_EXT_ORIGIN


async def test_cors_allows_localhost_origin(client) -> None:
    response = await client.options(
        "/v1/briefs/decode",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
