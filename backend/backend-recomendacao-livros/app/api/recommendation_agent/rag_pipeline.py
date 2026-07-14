import unicodedata

from sqlalchemy import String, cast, select

from app.models.livro import Livro
from app.services.embedding_service import embedding_service
from app.api.utils import Book

class RagPipeline:
    """
    Responsável por fazer a pipeline do RAG da aplicação.
    """
    
    def __init__(self):
        
        self.embedding_service = embedding_service
        self.genre_keywords = {
            "ROMANCE": {
                "amor",
                "romance",
                "romantico",
                "romantica",
                "relacionamento",
                "relacionamentos",
                "emocao",
                "emocional",
                "casal",
                "contemporaneo",
                "leve",
            },
            "FANTASIA": {
                "fantasia",
                "magia",
                "magico",
                "magica",
                "bruxo",
                "bruxa",
                "criatura",
                "criaturas",
                "mitologia",
                "mitologico",
                "mitologica",
                "aventura",
                "mundo imaginario",
                "mundo diferente",
            },
            "TERROR": {
                "terror",
                "horror",
                "sombrio",
                "sobrenatural",
                "vampiro",
                "medo",
                "assustador",
                "angustia",
            },
            "SUSPENSE": {
                "suspense",
                "misterio",
                "investigacao",
                "crime",
                "crimes",
                "segredo",
                "segredos",
                "reviravolta",
                "reviravoltas",
                "assassinato",
            },
            "BIOGRAFIA": {
                "biografia",
                "trajetoria real",
                "pessoa relevante",
                "historia real",
                "vida de",
                "inspiradora",
                "inspirador",
            },
            "CLASSICO": {
                "classico",
                "classica",
                "literatura",
                "literario",
                "literaria",
                "antigo",
                "antiga",
                "obra importante",
            },
            "INFANTIL": {
                "infantil",
                "crianca",
                "criancas",
                "curto",
                "divertido",
            },
            "FICCAO": {
                "ficcao",
                "futuro",
                "futuros",
                "sociedade",
                "distopia",
                "tecnologia",
                "criativa",
                "ideia criativa",
            },
            "CIENCIA": {
                "ciencia",
                "cientifico",
                "cientifica",
                "fisica",
                "universo",
                "tecnologia",
                "aprender",
                "acessivel",
            },
            "POEMA": {
                "poema",
                "poesia",
                "poetico",
                "poetica",
            },
        }
    

    async def stream_build(self, session, user_query: str, top_k: int) -> list[Book]:
        """
        Implementa a pipeline de RAG.

        :param session: sessão com o banco de dados.
        :param user_query: pergunta do usuário.
        :param top_k: limite de livros que serão recuperados do banco.

        :return lista de objetos Book recuperados, se houver.
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
            user_query=user_query,
            user_query_embeded=embedding,
            top_k=top_k
        )

        books = self.format_results(retrived_books)

        return books

        

    async def retrive_books_from_base(
        self,
        session,
        user_query: str,
        user_query_embeded,
        top_k: int,
    ): 
        """
        Recupera os livros da base de dados, ordenando por similaridade dos embeddings. 

        :param session: sssão com o banco de dados. 
        :param user_query_embeded: embedding gerado a partir da pergunta do usuário.
        :param top_k: limite de livros que serão recuperados.
        """ 

        print("Recuperando livros do banco...")

        expected_genres = self.infer_genres(user_query)
        distance = Livro.embedding.cosine_distance(user_query_embeded)
        books_by_id = {}

        if expected_genres:
            genre_query = (
                select(Livro)
                .where(Livro.embedding.is_not(None))
                .where(cast(Livro.genero, String).in_(expected_genres))
                .order_by(distance)
                .limit(top_k)
            )
            genre_result = await session.execute(genre_query)
            for book in genre_result.scalars():
                books_by_id[book.id] = book

            if not books_by_id:
                genre_fallback_query = (
                    select(Livro)
                    .where(cast(Livro.genero, String).in_(expected_genres))
                    .order_by(Livro.id)
                    .limit(top_k)
                )
                genre_fallback_result = await session.execute(
                    genre_fallback_query
                )
                for book in genre_fallback_result.scalars():
                    books_by_id[book.id] = book

        query = (
            select(Livro)
            .where(Livro.embedding.is_not(None))
            .order_by(
                distance
            )
            .limit(top_k * 2)
        )

        result = await session.execute(query)
        for book in result.scalars():
            books_by_id.setdefault(book.id, book)
            if len(books_by_id) >= top_k:
                break

        if not books_by_id:
            fallback_query = (
                select(Livro)
                .order_by(Livro.id)
                .limit(top_k)
            )
            fallback_result = await session.execute(fallback_query)
            for book in fallback_result.scalars():
                books_by_id[book.id] = book

        return list(books_by_id.values())

    @staticmethod
    def normalize_text(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value.lower())
        return "".join(
            char for char in normalized if not unicodedata.combining(char)
        )

    def infer_genres(self, user_query: str) -> list[str]:
        normalized_query = self.normalize_text(user_query)
        matches: list[tuple[int, str]] = []

        for genre, keywords in self.genre_keywords.items():
            score = sum(
                1 for keyword in keywords
                if self.normalize_text(keyword) in normalized_query
            )
            if score:
                matches.append((score, genre))

        matches.sort(key=lambda item: item[0], reverse=True)
        return [genre for _, genre in matches]

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
