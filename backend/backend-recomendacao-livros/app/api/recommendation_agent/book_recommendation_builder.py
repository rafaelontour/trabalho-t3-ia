from dataclasses import dataclass

from prompts.book_recomendation import BOOK_RECOMMENDATION
from providers.llama_provider import OllamaProvider
from rag_pipeline import RagPipeline

@dataclass
class Book:

    # id: int # ver se vamos precisar disso mesmo
    title: str
    img_url: str
    year: int

@dataclass
class BookRecommendationResult: 

    response: str
    retrieved_books: list[Book]


class BookRecommendationBuilder:
    """
    Classe responsável por gerir o fluxo de recomendação de livros.
    """

    def __init__(self, provider: OllamaProvider):
        
        self.final_prompt = BOOK_RECOMMENDATION

        self.provider = provider

        self.rag_pipeline = RagPipeline()

    def stream_build(self, user_message: str): 
        """
        Função que executa a pipeline de geração da resposta de recomendação dos livros. 
        """

        rag_result = None

        # Etapa 1: processar a pergunta do usuário:
        # chamar um método que faz algum tratamento na pergunta. Ex: remover stopwords, pegar palavras-chave,
        # pedir pra o modelo melhorar a pergunta
        # retornar as palavras chaves da pergunta para montar a query.

        # TODO: tirar o comentário quando a função estiver implementada        
        # improved_query = self.process_user_message(user_message)

        # Etapa 2: recuperar os documentos usando RAG
        rag_result = self.rag_pipeline.stream_build(
            session=...,
            user_message=user_message
        )

        # Etapa : fazer a injeção do contexto no prompt. 
        # substituir no prompt os placeholders:  catalogo_livros e pergunta_usuario
        updated_prompt = ""


        # Etapa 4: geração de resposta final
        response = self.provider.generate_response(
            prompt=updated_prompt
        )

        # TODO ajustar esse retorno de livros 
        return BookRecommendationResult(
            response=response,
            retrieved_books=[]
        )
    
    def process_user_message(user_message: str) -> str:
        """
        
        """
        # TODO: ajustar 


        improved_query = ""

        return improved_query

