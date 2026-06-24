# Decode Job Design: Synchronous vs. Asynchronous

## Current design: synchronous, inline decode

`POST /v1/briefs/decode` calls the LLM provider inline and returns the full
`DecodeRunResponse` (status = `completed` or `failed`) in a single HTTP round
trip. The database row is created and immediately updated before the response
is sent.

### Why sync is right for this product

| Factor | Synchronous (current) | Async job queue |
|---|---|---|
| Latency budget | GPT-4o-mini P50 ≈ 2-4 s — acceptable for a one-off popup action | Requires client polling or WebSocket; worse UX |
| Infrastructure complexity | Zero extra services | Needs a task broker (Celery/ARQ/Temporal) + workers |
| Operational surface | One process | At least three (API, broker, worker) |
| Failure recovery | Provider timeout raises HTTP 502 immediately | Dead-letter queues, retry policies, visibility timeouts |
| Test surface | Fully testable in-process | Worker isolation, message serialisation, idempotency across hops |

A brief decode is a **low-latency, single-tenant action** — the user is waiting
at the popup for a result. The added complexity of a job queue only pays off
when:

- Background processing is acceptable to the user (e.g. batch imports)
- Jobs are long-running (> 30 s) and need to survive server restarts
- Fan-out is required (one request triggers many parallel LLM calls)

None of those apply here.

## Provider timeout

`PROVIDER_TIMEOUT_SECONDS` (default 30 s, env-configurable) is passed to the
`ModelSettings` of the PydanticAI agent. If the LLM provider exceeds this
budget, the request fails with a `ProviderError` → HTTP 502. The client gets
fast failure feedback instead of an indefinitely hanging connection.

## When to revisit

Switch to async jobs if:

1. You add batch brief processing (multiple briefs per request)
2. The provider timeout is regularly exceeded in production
3. You need to store partial streaming results
4. You add human-in-the-loop review steps between decode stages
