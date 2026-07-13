from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.livro import Livro
from app.services.embedding_service import embedding_service
from app.api.utils import Book

class RagPipeline:
    """
    Responsável por fazer a pipeline do RAG da aplicação.
    """
    
    def __init__(self):
        
        self.embedding_service = embedding_service
    

    async def stream_build(self, session, user_query: str, top_k: int) -> list[Book]:
        """
        
        """

        print("Iniciando pipeline de recuperação dos livros...")

        print(f"Vetorizando a pergunta do usuário: '{user_query}'")
        # Etapa 1: fazer a vetorização da pergunta do usuário
        embedding = embedding_service.gerar_embedding(
            user_query
        )

        # Etapa 2: recuperar os livros da base de dados
        retrived_books = await self.retrive_books_from_base(
            session=session,
            user_query_embeded=embedding,
            top_k=top_k
        )

        books = self.format_results(retrived_books)

        return books

        

    async def retrive_books_from_base(self, session, user_query_embeded, top_k: int): 
        """
        Recupera os livros da base de dados, ordenando por similaridade dos embeddings. 

        :param session: sssão com o banco de dados. 
        :param user_query_embeded: embedding gerado a partir da pergunta do usuário.
        :param top_k: limite de livros que serão recuperados.
        """ 

        print("Recuperando livros do banco...")

        query = (
            select(Livro)
            .order_by(
                Livro.embedding.cosine_distance(user_query_embeded)
            )
            .limit(top_k)
        )

        result = await session.execute(query)

        return list(result.scalars())

    def format_results(self, results: list) -> list[Book]:
        """
        Formata os resultados recuperados do banco. 

        :param results: lista de livros recuperados.

        :return lista de livros formatados
        """

        formatted_results: list[Book] = []

        for book in results:

            formatted_book = Book(
                title=book.titulo,
                author=book.autor,
                year=book.ano,
                category=book.genero,
                number_of_pages=book.numero_paginas,
                book_description=book.descricao
            )
            formatted_results.append(formatted_book)

        return formatted_results


