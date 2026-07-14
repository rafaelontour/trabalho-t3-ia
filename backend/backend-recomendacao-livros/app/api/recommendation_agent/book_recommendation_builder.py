import logging

from dataclasses import dataclass

from app.db.session import AsyncSessionLocal
from app.prompts.book_recomendation import BOOK_RECOMMENDATION
from app.api.providers.llama_provider import OllamaProvider
from app.api.providers.gemini_provider import GeminiProvider
from app.api.providers.openai_provider import OpenAIProvider
from app.api.recommendation_agent.rag_pipeline import RagPipeline
from app.api.utils import BookRecommendationResult

logger = logging.getLogger("app_logger.book_recommendation_builder")


class BookRecommendationBuilder:
    """
    Classe responsável por gerir o fluxo de recomendação de livros.
    """

    def __init__(self, provider: OllamaProvider | GeminiProvider | OpenAIProvider):
        
        self.response_prompt = BOOK_RECOMMENDATION

        self.provider = provider

        self.rag_pipeline = RagPipeline()

    async def stream_build(self, user_message: str, top_k: int) -> BookRecommendationResult: 
        """
        Função que executa a pipeline de geração da resposta de recomendação dos livros. 
        """

        print("Iniciando pipeline do builder....")
        rag_result = None


        async with AsyncSessionLocal() as session:

            # Etapa 2: recuperar os documentos usando RAG
            rag_result = await self.rag_pipeline.stream_build(
                session=session,
                user_query=user_message,
                top_k=top_k
            )

        if not rag_result:

            logger.error(f"[BookRecommendationBuilder][stream_build] Erro: nenhum resultado retornado da RAGPipeline.")
            final_response = "Desculpe, tive um problema ao processar sua resposta e não encontrei nenhum livro no catálogo no momento."

            return BookRecommendationResult(
                response=final_response,
                retrieved_books=rag_result
            )

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

        final_response = ""

        try:
            for token in self.provider.generate_response_stream(prompt=updated_prompt):
                print(token, end="", flush=True)
                final_response += token
        
        except Exception:
            logger.exception(
                "[BookRecommendationBuilder][stream_build] Erro ao gerar "
                "resposta final. Usando resposta padrão."
            )
            return self.build_default_response(rag_result)

        if not final_response.strip():
            logger.error(
                "[BookRecommendationBuilder][stream_build] Provider não "
                "retornou tokens. Usando resposta padrão."
            )
            return self.build_default_response(rag_result)

        return BookRecommendationResult(
            response=final_response,
            retrieved_books=rag_result
        )
    
    def build_default_response(self, rag_documents: list) -> BookRecommendationResult:
        """
        Monta uma resposta padrão em caso de erro do llm, indicando para o usuário o livro 
        retornado que teve a maior similaridade na recuperação com o RAG.

        :param rag_documents: lista de documentos recuperados do banco.

        :return resposta final padrão montada.
        """

        # O RAG retorna os documentos ordenados por similaridade; o primeiro é o melhor
        best_result = rag_documents[0]

        # Monta uma resposta humanizada e informativa usando os dados do objeto Book
        response = (
            f"Tive um pequeno problema ao processar sua recomendação personalizada, mas com base na sua busca, "
            f"acredito que você possa gostar de **\"{best_result.title}\"**, escrito por {best_result.author} ({best_result.year}). "
            f"Este livro faz parte da categoria {best_result.normalize_category()} e sua sinopse diz: {best_result.book_description}"
        )

        return BookRecommendationResult(
            response=response,
            retrieved_books=[best_result]
        )
    


    def build_prompt(self, base_prompt: str, rag_documents: list, user_message: str) -> str:
        """
        Injeta o contexto no prompt base de resposta final. 

        :param base_prompt: prompt base da resposta, sem os documentos e a pergunta do usuário injetados.
        :param rag_documents: 

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
    
    async def stream_build_sem_rag(self, user_message: str, top_k: int):

        pass



# Teste do builder
if __name__ == "__main__": 

    import asyncio

    logging.basicConfig(level=logging.INFO)

    async def main(): 
        
        llama_provider = OllamaProvider(model_config={}) 
        gemini_provider = GeminiProvider(model_config={"temperature": 0.3, "token_limit": 300})
        openai_provider = OpenAIProvider(model_config={"temperature": 0.5, "token_limit": 200})

        builder = BookRecommendationBuilder(provider=gemini_provider)

        query = "Quero recomendações de livros de romance parecidos com os livros da Ali Hazelwood."

        response = await builder.stream_build(user_message=query, top_k=6)

        print(response)

    asyncio.run(main())
