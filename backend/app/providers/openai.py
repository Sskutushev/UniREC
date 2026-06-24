from __future__ import annotations

from pydantic_ai import Agent

from app.core.errors import ProviderError
from app.domain.schemas import BriefResult
from app.providers.base import LLMProvider, ProviderResponse

SYSTEM_PROMPT = """You convert raw client briefs into a strict JSON object.
Return only JSON that matches this schema:
- summary: non-empty string
- goals: non-empty string array
- deliverables: non-empty string array
- constraints: non-empty string array
- risks: non-empty array of { risk, severity(low|medium|high), reason }
- clarifying_questions: non-empty string array, every item ends with '?'
- recommended_next_action: non-empty string
"""


class OpenAIProvider(LLMProvider):
    def __init__(self, model_name: str) -> None:
        self._model_name = model_name
        self._agent = Agent(model_name, system_prompt=SYSTEM_PROMPT, result_type=BriefResult)

    @property
    def name(self) -> str:
        return "openai"

    async def decode_brief(self, text: str) -> ProviderResponse:
        try:
            result = await self._agent.run(text)
        except Exception as exc:  # pragma: no cover - network/provider path
            raise ProviderError("OpenAI provider request failed", error_code="provider_failure") from exc
        return ProviderResponse(raw_output=result.output.model_dump_json())
