import os
import logging
from typing import Generator
from dotenv import load_dotenv
from openai import OpenAI  # Importa o cliente oficial da OpenAI

logger = logging.getLogger("app_logger.openai_provider")

# Mantendo o mesmo caminho absoluto do seu projeto da UNEB
ENV_PATH = "/home/tatiana/uneb/trabalho-t3-ia/backend/backend-recomendacao-livros/.env"
load_dotenv(dotenv_path=ENV_PATH)

MAX_TOKENS_DEFAULT = 250
DEFAULT_TEMPERATURE = 0.7

class OpenAIProvider:
    """
    Provider para integração com a API da OpenAI (ChatGPT).
    """

    def __init__(self, model_config: dict = None):
        self.model_config = model_config if model_config is not None else {}
        
        # Modelo recomendado: gpt-4o-mini (é o mais rápido e barato atual)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        # O cliente busca automaticamente a variável OPENAI_API_KEY do seu .env
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError(
                f"A OPENAI_API_KEY não foi encontrada no arquivo .env localizado em: {ENV_PATH}"
            )
            
        self.client = OpenAI(api_key=api_key)

    def generate_response_stream(self, prompt: str) -> Generator[str, None, None]:
        """
        Faz uma requisição para a OpenAI enviando os blocos de texto por streaming em tempo real.
        """
        temperature = self.model_config.get("temperature", DEFAULT_TEMPERATURE)
        max_tokens = self.model_config.get("token_limit", MAX_TOKENS_DEFAULT)

        try:
            print(f"[OpenAIProvider] Iniciando geração por streaming com o modelo {self.model}...")

            # Chamada de chat completions oficial da OpenAI
            response_stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em livros."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True  # Ativa o recebimento em tempo real
            )

            # Itera sobre os pedaços (chunks) assim que eles chegam da API
            for chunk in response_stream:
                # Na OpenAI, precisamos checar se o texto existe dentro das estruturas 'choices'
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.exception(f"[OpenAIProvider] Erro na geração via OpenAI: {e}")
            raise


# TESTE DO PROVIDER DA OPENAI
if __name__ == "__main__":
    # Configuração para ver o teste no terminal
    logging.basicConfig(level=logging.INFO)
    
    # Lembre-se de adicionar no seu .env:
    # OPENAI_API_KEY=sk-...
    # OPENAI_MODEL=gpt-4o-mini
    
    provider = OpenAIProvider(model_config={"temperature": 0.5, "token_limit": 200})

    print("Resposta da OpenAI: ", end="", flush=True)
    for token in provider.generate_response_stream(prompt="Me indique um livro de suspense psicológico."):
        print(token, end="", flush=True)
    print()
