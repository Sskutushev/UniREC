from app.core.config import Settings
from app.providers.base import LLMProvider
from app.providers.fake import FakeProvider
from app.providers.openai import OpenAIProvider


def build_provider(settings: Settings) -> LLMProvider:
    timeout = settings.provider_timeout_seconds
    if settings.provider == "fake":
        return FakeProvider(mode=settings.fake_provider_mode, timeout_seconds=timeout)
    if settings.provider == "openai":
        return OpenAIProvider(model_name=settings.openai_model_name, timeout_seconds=timeout)
    raise ValueError(f"Unknown provider: {settings.provider}")
