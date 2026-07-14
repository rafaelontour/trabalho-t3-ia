import asyncio
import sys

from sqlalchemy import func, select

from app.db.session import AsyncSessionLocal
from app.models.livro import Livro
from app.services.embedding_service import embedding_service


CONSULTAS_PADRAO = [
    "quero um livro da ali hazelwood",
    "fantasia com magia e aventura",
    "terror com vampiros",
    "livros de ciencia sobre o universo",
]


def assinatura_embedding(embedding: list[float]) -> str:
    primeiros = ", ".join(f"{valor:.4f}" for valor in embedding[:8])
    soma = sum(embedding)
    norma_quadrada = sum(valor * valor for valor in embedding)
    return (
        f"primeiros=[{primeiros}] | "
        f"soma={soma:.4f} | "
        f"norma^2={norma_quadrada:.4f}"
    )


async def contar_embeddings(session) -> None:
    total_query = select(func.count()).select_from(Livro)
    com_embedding_query = (
        select(func.count())
        .select_from(Livro)
        .where(Livro.embedding.is_not(None))
    )

    total = await session.scalar(total_query)
    com_embedding = await session.scalar(com_embedding_query)

    print(f"Livros no banco: {total}")
    print(f"Livros com embedding: {com_embedding}")


async def imprimir_ranking(session, user_query: str, limite: int = 10) -> None:
    embedding = embedding_service.gerar_embedding(user_query)
    print("\n" + "=" * 80)
    print(f"Consulta: {user_query!r}")
    print(f"Dimensoes do embedding da pergunta: {len(embedding)}")
    print(f"Assinatura do embedding: {assinatura_embedding(embedding)}")

    distancia = Livro.embedding.cosine_distance(embedding)
    similaridade = (1 - distancia).label("similaridade")

    query = (
        select(
            Livro,
            distancia.label("distancia"),
            similaridade,
        )
        .where(Livro.embedding.is_not(None))
        .order_by(distancia)
        .limit(limite)
    )

    results = await session.execute(query)
    livros_recuperados = results.all()

    if not livros_recuperados:
        print("Nenhum livro com embedding foi encontrado no banco.")
        return

    print(f"\nTop {limite} livros por similaridade no pgvector:\n")

    for posicao, (livro, distancia_valor, similaridade_valor) in enumerate(
        livros_recuperados,
        start=1,
    ):
        print(
            f"{posicao:02d}. {livro.titulo} | {livro.autor} | "
            f"{livro.genero} | "
            f"distancia={distancia_valor:.4f} | "
            f"similaridade={similaridade_valor:.4f}"
        )


async def main():
    consultas = sys.argv[1:] or CONSULTAS_PADRAO

    async with AsyncSessionLocal() as session:
        await contar_embeddings(session)

        for consulta in consultas:
            await imprimir_ranking(session, consulta)


if __name__ == "__main__":
    asyncio.run(main())
