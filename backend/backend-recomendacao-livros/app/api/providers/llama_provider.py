import os
import ollama
import logging

from dotenv import load_dotenv

logger = logging.getLogger("app_logger.ollama_provider")


load_dotenv()

MAX_TOKENS_DEFAULT = 250
DEFAULT_TEMPERATURE = 0.7

class OllamaProvider:
    """
    Provider 
    """

    def __init__(self, model_config: dict):
        
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2")
        self.url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.client = ollama.Client(host=self.url)
        self.model_config = model_config

    def generate_response(self, prompt: str):

        """
        Função que faz um request ao modelo e retorna a reposta gerada, sem streaming.

        :param str prompt: user_prompt passado.
        :param dict model_config: configurações do modelo. 

        :return str resposta do modelo. 
        """
        
        temperature = self.model_config.get("temperature", DEFAULT_TEMPERATURE)
        max_tokens = self.model_config.get("token_limit", MAX_TOKENS_DEFAULT)

        try: 
            
            # TODO: mudar para logger depois que arrumar -> colocar no main ou no app logging.basicConfig(level=logging.INFO)
            print(f"[OllamaProvider][generate_response] Iniciando geração de resposta...")

            response = self.client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em livros."},
                    {"role": "user", "content": prompt}
                ],
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens # No Ollama nativo, 'max_tokens' se chama 'num_predict'
                },
                stream=False
            )

            if response:
                response_content = response['message']['content']
                print(f"[OllamaProvider][generate_response] Resposta gerada pelo modelo: {response_content}")

                # TODO: loggers com problema, nivel INFO não esta mostrando no terminal, apenas exception
                logger.info(f"[OllamaProvider][generate_response] Resposta gerada pelo modelo: {response_content}")

        except Exception as e: 
            
            logger.exception(f"[OllamaProvider][generate_response] Erro ao carregar a resposta do modelo: {e}")


# TESTE DO PROVIDER
if __name__ == "__main__": 


    provider = OllamaProvider()

    response = provider.generate_response(prompt="Me indique um livro de romance", model_config={})
