from uuid import uuid4

BRIEF_TEXT = (
    "We need a landing page for a B2B SaaS analytics product. "
    "The page should explain the product, include pricing teaser, "
    "capture emails, and be ready in 2 weeks. Budget is limited."
)


async def test_get_run_status_matches_created_run(client) -> None:
    create_response = await client.post("/v1/briefs/decode", json={"text": BRIEF_TEXT})
    run_id = create_response.json()["run_id"]

    get_response = await client.get(f"/v1/briefs/runs/{run_id}")

    assert get_response.status_code == 200
    assert get_response.json()["run_id"] == run_id
    assert get_response.json()["status"] == "completed"


async def test_get_unknown_run_returns_404(client) -> None:
    response = await client.get(f"/v1/briefs/runs/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["error_code"] == "run_not_found"


async def test_second_identical_request_reuses_cached_result(client) -> None:
    first_response = await client.post("/v1/briefs/decode", json={"text": BRIEF_TEXT})
    second_response = await client.post("/v1/briefs/decode", json={"text": BRIEF_TEXT})

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.json()["run_id"] != second_response.json()["run_id"]
    assert first_response.json()["result"] == second_response.json()["result"]
