from html import escape
from urllib.parse import quote_plus

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.models.livro import Livro
from app.repositories.livro_repository import LivroRepository
from app.schemas.livro import LivroListResponse, LivroResponse

router = APIRouter(prefix="/livros", tags=["Livros"])

GENEROS_LIVRO = [
    "ROMANCE",
    "FANTASIA",
    "FICCAO",
    "TERROR",
    "SUSPENSE",
    "CIENCIA",
    "BIOGRAFIA",
    "CLASSICO",
    "INFANTIL",
    "POEMA",
    "OUTRO",
]

GENERO_CORES = {
    "ROMANCE": ("#b83265", "#ffe0ea"),
    "FANTASIA": ("#4c3f91", "#e8e3ff"),
    "FICCAO": ("#1f6f8b", "#dff6ff"),
    "TERROR": ("#2b2024", "#ffd6dc"),
    "SUSPENSE": ("#5b3a29", "#f4dfcf"),
    "CIENCIA": ("#1f7a5c", "#ddf7ec"),
    "BIOGRAFIA": ("#6a4c2f", "#f3e7d4"),
    "CLASSICO": ("#6d6238", "#f4efcf"),
    "INFANTIL": ("#cc6b2c", "#ffead7"),
    "POEMA": ("#7a3b69", "#f7def0"),
    "OUTRO": ("#2e5d48", "#e4f0ea"),
}


def imagem_url_livro(livro_id: str) -> str:
    return (
        f"{settings.public_base_url.rstrip('/')}"
        f"{settings.api_prefix}/livros/{livro_id}/capa"
    )


def imagem_padrao_url_livro(livro_id: str) -> str:
    return (
        f"{settings.public_base_url.rstrip('/')}"
        f"{settings.api_prefix}/livros/{livro_id}/capa.svg"
    )


def livro_response(livro: Livro) -> LivroResponse:
    response = LivroResponse.model_validate(livro)
    response.imagem_url = imagem_url_livro(livro.id)
    return response


def quebrar_titulo(titulo: str, limite: int = 18) -> list[str]:
    linhas: list[str] = []
    atual = ""

    for palavra in titulo.split():
        candidato = f"{atual} {palavra}".strip()
        if len(candidato) <= limite:
            atual = candidato
            continue

        if atual:
            linhas.append(atual)
        atual = palavra

        if len(linhas) == 3:
            break

    if atual and len(linhas) < 3:
        linhas.append(atual)

    return linhas[:3] or ["Livro"]


@router.get("", response_model=LivroListResponse)
async def listar_livros(
    limite: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    busca: str | None = Query(default=None, min_length=1, max_length=120),
    genero: str | None = Query(default=None, min_length=1, max_length=40),
    db: AsyncSession = Depends(get_db),
) -> LivroListResponse:
    repository = LivroRepository(db)
    busca_normalizada = busca.strip() if busca else None
    genero_normalizado = genero.strip().upper() if genero else None
    livros = await repository.listar(
        limite=limite,
        offset=offset,
        busca=busca_normalizada,
        genero=genero_normalizado,
    )
    total = await repository.contar(
        busca=busca_normalizada,
        genero=genero_normalizado,
    )

    return LivroListResponse(
        items=[livro_response(livro) for livro in livros],
        total=total,
        limite=limite,
        offset=offset,
    )


@router.get("/generos", response_model=list[str])
async def listar_generos() -> list[str]:
    return GENEROS_LIVRO


@router.get("/{livro_id}/capa", response_class=RedirectResponse)
async def buscar_capa_livro(
    livro_id: str,
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    repository = LivroRepository(db)
    livro = await repository.buscar_por_id(livro_id)

    if livro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livro não encontrado.",
        )

    termos = " ".join(
        parte for parte in [livro.titulo, livro.autor] if parte
    )
    url_busca = (
        "https://openlibrary.org/search.json"
        f"?q={quote_plus(termos)}&limit=5"
    )
    imagem = None

    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            response = await client.get(url_busca)
            response.raise_for_status()
            data = response.json()
    except Exception:
        data = {}

    for item in data.get("docs", []):
        cover_id = item.get("cover_i")
        if cover_id:
            imagem = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
            break

    if not imagem:
        imagem = imagem_padrao_url_livro(livro.id)

    return RedirectResponse(
        url=imagem.replace("http://", "https://"),
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )


@router.get("/{livro_id}/capa.svg", response_class=Response)
async def gerar_capa_livro(
    livro_id: str,
    db: AsyncSession = Depends(get_db),
) -> Response:
    repository = LivroRepository(db)
    livro = await repository.buscar_por_id(livro_id)

    if livro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livro não encontrado.",
        )

    genero = livro.genero or "OUTRO"
    cor, fundo = GENERO_CORES.get(genero, GENERO_CORES["OUTRO"])
    titulo_linhas = quebrar_titulo(livro.titulo or "Livro sem título")
    autor = escape(livro.autor or "Autor não informado")
    genero_texto = escape(genero)
    linhas_svg = "\n".join(
        f'<text x="32" y="{150 + indice * 34}" class="title">'
        f"{escape(linha)}</text>"
        for indice, linha in enumerate(titulo_linhas)
    )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="360" height="520" viewBox="0 0 360 520" role="img">
  <style>
    .genre {{ font: 700 18px Arial, sans-serif; letter-spacing: 2px; }}
    .title {{ font: 800 30px Arial, sans-serif; }}
    .author {{ font: 600 18px Arial, sans-serif; }}
  </style>
  <rect width="360" height="520" fill="{fundo}"/>
  <rect x="22" y="22" width="316" height="476" rx="18" fill="#ffffff" opacity="0.78"/>
  <rect x="32" y="32" width="296" height="456" rx="14" fill="{cor}"/>
  <circle cx="286" cy="84" r="42" fill="#ffffff" opacity="0.16"/>
  <circle cx="70" cy="420" r="62" fill="#ffffff" opacity="0.12"/>
  <text x="32" y="92" class="genre" fill="#ffffff" opacity="0.9">{genero_texto}</text>
  {linhas_svg}
  <text x="32" y="440" class="author" fill="#ffffff" opacity="0.9">{autor}</text>
</svg>"""

    return Response(
        content=svg,
        media_type="image/svg+xml",
        headers={"Cache-Control": "public, max-age=86400"},
    )


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

    return livro_response(livro)
