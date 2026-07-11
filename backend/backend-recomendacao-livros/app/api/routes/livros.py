from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.livro_repository import LivroRepository
from app.schemas.livro import LivroResponse

router = APIRouter(prefix="/livros", tags=["Livros"])


@router.get("", response_model=list[LivroResponse])
async def listar_livros(
    limite: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> list[LivroResponse]:
    repository = LivroRepository(db)
    livros = await repository.listar(limite=limite, offset=offset)
    return [LivroResponse.model_validate(livro) for livro in livros]


@router.get("/{livro_id}", response_model=LivroResponse)
async def buscar_livro(
    livro_id: str,
    db: AsyncSession = Depends(get_db),
) -> LivroResponse:
    repository = LivroRepository(db)
    livro = await repository.buscar_por_id(livro_id)

    if livro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livro não encontrado.",
        )

    return LivroResponse.model_validate(livro)
