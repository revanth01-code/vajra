import anthropic

from src.config.env import settings


def get_anthropic_client() -> anthropic.Anthropic | None:
    if settings.anthropic_api_key is None:
        return None
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)
