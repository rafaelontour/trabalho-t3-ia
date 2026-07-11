import os
import ollama
import logging

from dotenv import load_dotenv

logger = logging.getLogger("app_logger.ollama_provider")


load_dotenv('../api/app/.env')

MAX_TOKENS_DEFAULT = 250
DEFAULT_TEMPERATURE = 0.7

class OllamaProvider:
    """

    """

    def __init__(self):
        
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2")
        self.api_key = os.getenv("OLLAMA_API_KEY", "")
        self.url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

        self.client = ollama.Client(host=self.url)

    def generate_response(self, prompt: str, model_config: dict):

        temperature = model_config.get("temperature", DEFAULT_TEMPERATURE)
        max_tokens = model_config.get("token_limit", MAX_TOKENS_DEFAULT)

        try: 

            chat_completion = client.chat.completions.create(
                model=OLLAMA_MODEL, # Use o nome do seu modelo local Ollama
                messages=[
                    {"role": "system", "content": "Você é um assistente útil."},
                    {"role": "user", "content": "Explique a diferença entre Ollama e llama.cpp."}
                ],
                temperature=0.7,
                max_tokens=250, # Nota: 'max_tokens' corresponde aproximadamente a 'num_predict' do Ollama
                stream=False # Defina como True para respostas em streaming
            )

            if chat_completion:

                logger.info(f"[OllamaProvider][generate_response] ")

        except Exception as e: 
            
            logger.exception(f"[OllamaProvider][generate_response] Erro ao carregar a resposta do modelo: {e}")

            






# Certifique-se de ter a biblioteca openai instalada: pip install openai
from openai import OpenAI
import os

# Defina o endpoint Ollama e uma chave API fictícia
OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_API_KEY = "ollama" # Placeholder, valor ignorado pelo Ollama

# Especifique o modelo local Ollama que você deseja usar
OLLAMA_MODEL = "llama3.2"

try:
    # Inicialize o cliente OpenAI, apontando-o para o servidor Ollama
    client = OpenAI(
        base_url=OLLAMA_BASE_URL,
        api_key=OLLAMA_API_KEY,
    )

    print(f"Enviando requisição para o modelo Ollama: {OLLAMA_MODEL} via camada de compatibilidade OpenAI...")

    # Faça uma requisição padrão de completude de chat
    chat_completion = client.chat.completions.create(
        model=OLLAMA_MODEL, # Use o nome do seu modelo local Ollama
        messages=[
            {"role": "system", "content": "Você é um assistente útil."},
            {"role": "user", "content": "Explique a diferença entre Ollama e llama.cpp."}
        ],
        temperature=0.7,
        max_tokens=250, # Nota: 'max_tokens' corresponde aproximadamente a 'num_predict' do Ollama
        stream=False # Defina como True para respostas em streaming
    )

    # Processe a resposta
    if chat_completion.choices:
        response_content = chat_completion.choices[0].message.content
        print("\nResposta Ollama:")
        print(response_content)
        print("\nEstatísticas de Uso:")
        print(f"  Tokens de Prompt: {chat_completion.usage.prompt_tokens}")
        print(f"  Tokens de Completude: {chat_completion.usage.completion_tokens}")
        print(f"  Tokens Totais: {chat_completion.usage.total_tokens}")
    else:
        print("Nenhuma opção de resposta recebida do Ollama.")

except Exception as e:
    print(f"\nOcorreu um erro:")
    print(f"  Tipo de Erro: {type(e).__name__}")
    print(f"  Detalhes do Erro: {e}")
    print(f"\nPor favor, certifique-se de que o servidor Ollama está executando e acessível em {OLLAMA_BASE_URL}.")
    print(f"Verifique também se o modelo '{OLLAMA_MODEL}' está disponível localmente ('ollama list').")