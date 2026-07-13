import os
import logging
from typing import Generator
from dotenv import load_dotenv
from google import genai
from google.genai import types

logger = logging.getLogger("app_logger.gemini_provider")

# load_dotenv('../api/app/.env')

ENV_PATH = "/home/tatiana/uneb/trabalho-t3-ia/backend/backend-recomendacao-livros/.env"
load_dotenv(dotenv_path=ENV_PATH)

MAX_TOKENS_DEFAULT = 250
DEFAULT_TEMPERATURE = 0.7

class GeminiProvider:
    """
    Provider para integração com a API do Google Gemini.
    """

    def __init__(self, model_config: dict = None):
        self.model_config = model_config if model_config is not None else {}
        
        # Modelo padrão rápido (Flash). Você pode usar 'gemini-2.5-flash' ou 'gemini-3.5-flash'
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError(
                "A GEMINI_API_KEY não foi encontrada no arquivo .env. "
                "Verifique se o caminho '../api/app/.env' está correto."
            )

        # O cliente busca automaticamente a variável de ambiente GEMINI_API_KEY
        self.client = genai.Client(api_key=api_key)

    def generate_response_stream(self, prompt: str) -> Generator[str, None, None]:
        """
        Faz uma requisição ao Gemini enviando os blocos de texto por streaming em tempo real.
        """
        temperature = self.model_config.get("temperature", DEFAULT_TEMPERATURE)
        max_tokens = self.model_config.get("token_limit", MAX_TOKENS_DEFAULT)

        # No SDK do Gemini, instruções do sistema e parâmetros ficam no GenerateContentConfig
        config = types.GenerateContentConfig(
            system_instruction="Você é um assistente especializado em livros.",
            temperature=temperature,
            max_output_tokens=max_tokens
        )

        try:
            print(f"[GeminiProvider] Iniciando geração por streaming com o modelo {self.model}...")

            # Chamada de streaming oficial do SDK
            response_stream = self.client.models.generate_content_stream(
                model=self.model,
                contents=prompt,
                config=config
            )

            # Envia cada pedaço assim que chega da nuvem da Google
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            logger.exception(f"[GeminiProvider] Erro na geração via Gemini: {e}")


# TESTE DO PROVIDER DO GEMINI
if __name__ == "__main__":
    # IMPORTANTE: Garanta que você tenha colocado a chave no seu .env ou ambiente:
    # export GEMINI_API_KEY="sua_chave_aqui"
    
    provider = GeminiProvider(model_config={"temperature": 0.3, "token_limit": 300})

    print("Resposta do Gemini: ", end="", flush=True)
    for token in provider.generate_response_stream(prompt="Me indique um livro de ficção científica rápido de ler."):
        print(token, end="", flush=True)
    print()