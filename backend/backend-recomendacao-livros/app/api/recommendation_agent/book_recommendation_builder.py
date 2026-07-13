from dataclasses import dataclass

from app.db.session import AsyncSessionLocal
from app.prompts.book_recomendation import BOOK_RECOMMENDATION
from app.api.providers.llama_provider import OllamaProvider
from app.api.recommendation_agent.rag_pipeline import RagPipeline
from app.api.utils import Book

@dataclass
class BookRecommendationResult: 

    response: str
    retrieved_books: list[Book]


class BookRecommendationBuilder:
    """
    Classe responsável por gerir o fluxo de recomendação de livros.
    """

    def __init__(self, provider: OllamaProvider):
        
        self.response_prompt = BOOK_RECOMMENDATION

        self.provider = provider

        self.rag_pipeline = RagPipeline()

    async def stream_build(self, user_message: str, top_k: int) -> BookRecommendationResult: 
        """
        Função que executa a pipeline de geração da resposta de recomendação dos livros. 
        """

        print("Iniciando pipeline do builder....")
        rag_result = None

        # Etapa 1: processar a pergunta do usuário:
        # chamar um método que faz algum tratamento na pergunta. Ex: remover stopwords, pegar palavras-chave,
        # pedir pra o modelo melhorar a pergunta
        # retornar as palavras chaves da pergunta para montar a query.
        # TODO: tirar o comentário quando a função estiver implementada        
        # improved_query = self.process_user_message(user_message)

        async with AsyncSessionLocal() as session:

            # Etapa 2: recuperar os documentos usando RAG
            rag_result = await self.rag_pipeline.stream_build(
                session=session,
                user_query=user_message,
                top_k=top_k
            )

        if not rag_result:
            raise (f"[][] Erro: nenhum resultado retornado da RAGPipeline.")

        print("Livros recuperados da RagPipeline...")

        # Etapa : fazer a injeção do contexto no prompt. 
        # substituir no prompt os placeholders:  catalogo_livros e pergunta_usuario
        updated_prompt = self.build_prompt(
            base_prompt=self.response_prompt,
            rag_documents=rag_result,
            user_message=user_message
        )

        print("Gerando a resposta final...")
        # Etapa 4: geração de resposta final
        response = self.provider.generate_response(
            prompt=updated_prompt
        )

        return BookRecommendationResult(
            response=response,
            retrieved_books=rag_result
        )
    
    def build_prompt(self, base_prompt: str, rag_documents: list, user_message: str) -> str:
        """
        Injeta o contexto no prompt base de resposta final. 

        :param 
        :param 

        :return 
        """

        # Usar list comprehension + join é mais rápido e limpo que loops com +=
        livros_formatados = [book.to_prompt_format() for book in rag_documents]
        
        # Separador visual limpo usando Markdown (---)
        catalogo_livros = "\n\n---\n\n".join(livros_formatados)

        return base_prompt.format(
            catalogo_livros=catalogo_livros,
            pergunta_usuario=user_message.strip(),
        )

    
    # def process_user_message(user_message: str) -> str:
    #     """
        
    #     """
    #     # TODO: ajustar 


    #     improved_query = ""

    #     return improved_query

if __name__ == "__main__": 

    import asyncio

    async def main(): 
        llama_provider = OllamaProvider(model_config={}) 

        builder = BookRecommendationBuilder(provider=llama_provider)

        query = "Quero recomendações de livro da Ali Hazelwood."

        response = await builder.stream_build(user_message=query, top_k=6)

        print(response)

    asyncio.run(main())