from typing import Any

from app.api.providers.gemini_provider import GeminiProvider
from app.api.providers.llama_provider import OllamaProvider
from app.api.providers.openai_provider import OpenAIProvider


def create_provider(
    provider_name: str,
    model_config: dict[str, Any] | None = None,
):
    """Cria apenas o provider solicitado pelo experimento."""
    normalized_name = provider_name.strip().lower()
    config = model_config or {}

    if normalized_name == "openai":
        return OpenAIProvider(model_config=config)

    if normalized_name == "gemini":
        return GeminiProvider(model_config=config)

    if normalized_name == "ollama":
        return OllamaProvider(model_config=config)

    raise ValueError(
        "Provider inválido. Utilize 'openai', 'gemini' ou 'ollama'."
    )
