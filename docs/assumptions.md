# Assumptions

- The prototype optimizes for local reproducibility first.
- The fake provider is the default provider and must work without secrets.
- The current API is synchronous, but the run model is intentionally future-proofed for queue-based async execution.
- E2E validation focuses on the backend and extension slices that are critical for the assignment.
