from __future__ import annotations

import asyncio
import json

from app.core.errors import ProviderError
from app.providers.base import LLMProvider, ProviderResponse


class FakeProvider(LLMProvider):
    def __init__(self, mode: str = "valid") -> None:
        self._mode = mode

    @property
    def name(self) -> str:
        return "fake"

    async def decode_brief(self, text: str) -> ProviderResponse:
        await asyncio.sleep(0.1)

        if self._mode == "provider_error":
            raise ProviderError("Provider execution failed", error_code="provider_failure")
        if self._mode == "invalid_json":
            return ProviderResponse(raw_output='{"summary": "broken"')
        if self._mode == "invalid_severity":
            return ProviderResponse(
                raw_output=json.dumps(
                    {
                        **self._base_payload(text),
                        "risks": [
                            {
                                "risk": "Budget pressure may reduce scope clarity",
                                "severity": "critical",
                                "reason": "The brief signals limited budget and broad asks.",
                            }
                        ],
                    }
                )
            )
        if self._mode == "missing_fields":
            payload = self._base_payload(text)
            payload.pop("summary")
            return ProviderResponse(raw_output=json.dumps(payload))

        return ProviderResponse(raw_output=json.dumps(self._base_payload(text)))

    def _base_payload(self, text: str) -> dict[str, object]:
        topic = "landing page" if "landing page" in text.lower() else "client request"
        return {
            "summary": f"The client needs a {topic} decoded into a delivery-ready plan.",
            "goals": [
                "Explain the offer in simple B2B language",
                "Capture leads with a focused conversion path",
            ],
            "deliverables": [
                "Normalized brief summary",
                "Recommended delivery checklist",
            ],
            "constraints": [
                "Timeline is tight",
                "Budget needs careful prioritization",
            ],
            "risks": [
                {
                    "risk": "The requested scope may exceed the timeline",
                    "severity": "medium",
                    "reason": "The brief bundles content, SEO, and launch readiness into two weeks.",
                }
            ],
            "clarifying_questions": [
                "What is the primary conversion action for the page?",
                "Which SEO targets matter most for launch?",
            ],
            "recommended_next_action": "Confirm the main CTA, audience, and must-have launch content.",
        }
