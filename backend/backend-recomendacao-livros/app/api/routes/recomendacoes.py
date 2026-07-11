from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.db.session import get_db
from app.repositories.livro_repository import LivroRepository
from app.schemas.recomendacao import (
    RecomendacaoRequest,
    RecomendacaoResponse,
)
from app.services.embedding_service import embedding_service

router = APIRouter(prefix="/recomendacoes", tags=["Recomendações"])


@router.post("", response_model=list[RecomendacaoResponse])
async def recomendar_livros(
    payload: RecomendacaoRequest,
    db: AsyncSession = Depends(get_db),
) -> list[RecomendacaoResponse]:
    vetor_consulta = await run_in_threadpool(
        embedding_service.gerar_embedding,
        payload.preferencia,
    )

    repository = LivroRepository(db)
    resultados = await repository.buscar_semelhantes(
        embedding=vetor_consulta,
        limite=payload.limite,
    )

    return [
        RecomendacaoResponse(
            id=livro.id,
            titulo=livro.titulo,
            autor=livro.autor,
            genero=livro.genero,
            ano=livro.ano,
            numero_paginas=livro.numero_paginas,
            descricao=livro.descricao,
            similaridade=round(float(similaridade), 4),
        )
        for livro, similaridade in resultados
    ]
