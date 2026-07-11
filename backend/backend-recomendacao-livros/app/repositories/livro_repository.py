from sqlalchemy import String, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.livro import Livro


class LivroRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _aplicar_filtros(self, statement, busca: str | None, genero: str | None):
        if busca:
            termo = f"%{busca}%"
            statement = statement.where(Livro.titulo.ilike(termo))

        if genero:
            statement = statement.where(cast(Livro.genero, String) == genero)

        return statement

    async def listar(
        self,
        limite: int,
        offset: int,
        busca: str | None = None,
        genero: str | None = None,
    ) -> list[Livro]:
        statement = (
            self._aplicar_filtros(select(Livro), busca, genero)
            .order_by(Livro.titulo.asc())
            .offset(offset)
            .limit(limite)
        )
        result = await self.db.execute(statement)
        return list(result.scalars().all())

    async def contar(
        self,
        busca: str | None = None,
        genero: str | None = None,
    ) -> int:
        statement = self._aplicar_filtros(
            select(func.count()).select_from(Livro),
            busca,
            genero,
        )
        result = await self.db.execute(statement)
        return int(result.scalar_one())

    async def listar_generos(self) -> list[str]:
        statement = (
            select(cast(Livro.genero, String))
            .where(Livro.genero.is_not(None))
            .distinct()
            .order_by(cast(Livro.genero, String).asc())
        )
        result = await self.db.execute(statement)
        return [genero for genero in result.scalars().all() if genero]

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
