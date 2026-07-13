import asyncio

from sqlalchemy import select
from starlette.concurrency import run_in_threadpool

from app.db.session import AsyncSessionLocal
from app.models.livro import Livro
from app.services.embedding_service import embedding_service


def build_document(livro):

    return f"""
            Título: {livro.titulo}

            Autor: {livro.autor}

            Gênero: {livro.genero}

            Ano: {livro.ano}

            Número de páginas: {livro.numero_paginas}

            Descrição:
            {livro.descricao}
        """

def montar_texto(livro: Livro) -> str:
    partes = [
        livro.titulo,
        livro.autor,
        livro.genero,
        livro.descricao,
    ]
    return ". ".join(parte.strip() for parte in partes if parte and parte.strip())


async def main() -> None:
    embedding_service.load_model()

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Livro)
            .where(Livro.embedding.is_(None))
            .order_by(Livro.id)
        )
        livros = list(result.scalars().all())

        if not livros:
            print("Todos os livros já possuem embedding.")
            return

        for indice, livro in enumerate(livros, start=1):
            
            texto = build_document(livro)

            if not texto:
                print(f"Ignorado {livro.id}: não possui texto.")
                continue

            livro.embedding = await run_in_threadpool(
                embedding_service.gerar_embedding,
                texto,
            )
            print(f"[{indice}/{len(livros)}] {livro.titulo}")

        await db.commit()
        print(f"{len(livros)} embeddings processados.")


if __name__ == "__main__":
    asyncio.run(main())
