from app.core.config import Settings
from app.providers.base import LLMProvider
from app.providers.fake import FakeProvider
from app.providers.openai import OpenAIProvider


def build_provider(settings: Settings) -> LLMProvider:
    if settings.provider == "fake":
        return FakeProvider(mode=settings.fake_provider_mode)
    if settings.provider == "openai":
        return OpenAIProvider(model_name="openai:gpt-4o-mini")
    raise ValueError(f"Unknown provider: {settings.provider}")
