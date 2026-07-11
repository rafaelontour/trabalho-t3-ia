from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.livro import Livro


class LivroRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def listar(self, limite: int, offset: int) -> list[Livro]:
        statement = (
            select(Livro)
            .order_by(Livro.titulo.asc())
            .offset(offset)
            .limit(limite)
        )
        result = await self.db.execute(statement)
        return list(result.scalars().all())

    async def buscar_por_id(self, livro_id: str) -> Livro | None:
        return await self.db.get(Livro, livro_id)

    async def buscar_semelhantes(
        self,
        embedding: list[float],
        limite: int,
    ) -> list[tuple[Livro, float]]:
        distancia = Livro.embedding.cosine_distance(embedding)
        similaridade = (1 - distancia).label("similaridade")

        statement = (
            select(Livro, similaridade)
            .where(Livro.embedding.is_not(None))
            .order_by(distancia)
            .limit(limite)
        )

        result = await self.db.execute(statement)
        return [(row[0], float(row[1])) for row in result.all()]

    async def listar_sem_embedding(self) -> list[Livro]:
        statement = (
            select(Livro)
            .where(Livro.embedding.is_(None))
            .order_by(Livro.id)
        )
        result = await self.db.execute(statement)
        return list(result.scalars().all())
