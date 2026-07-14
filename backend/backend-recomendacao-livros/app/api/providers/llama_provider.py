import logging
import os
from collections.abc import Generator

import ollama
from dotenv import load_dotenv

logger = logging.getLogger("app_logger.ollama_provider")


load_dotenv()

MAX_TOKENS_DEFAULT = 250
DEFAULT_TEMPERATURE = 0.7

class OllamaProvider:
    """Provider para integração com um servidor local do Ollama."""

    def __init__(self, model_config: dict | None = None):
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2")
        self.url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.client = ollama.Client(host=self.url)
        self.model_config = model_config or {}

    def generate_response_stream(self, prompt: str) -> Generator[str, None, None]:
        """Gera a resposta em streaming, mantendo a interface dos demais providers."""
        temperature = self.model_config.get("temperature", DEFAULT_TEMPERATURE)
        max_tokens = self.model_config.get("token_limit", MAX_TOKENS_DEFAULT)

        try:
            response_stream = self.client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um assistente especializado em livros.",
                    },
                    {"role": "user", "content": prompt},
                ],
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
                stream=True,
            )

            for chunk in response_stream:
                content = chunk.get("message", {}).get("content")
                if content:
                    yield content
        except Exception as exc:
            logger.exception(
                "[OllamaProvider] Erro na geração via Ollama: %s", exc
            )
            raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    provider = OllamaProvider(
        model_config={"temperature": 0.3, "token_limit": 300}
    )

    print("Resposta do Ollama: ", end="", flush=True)
    for token in provider.generate_response_stream(
        prompt="Me indique um livro de romance."
    ):
        print(token, end="", flush=True)
    print()
