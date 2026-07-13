from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.db.session import get_db
from app.repositories.livro_repository import LivroRepository
from app.api.routes.livros import imagem_url_livro
from app.schemas.recomendacao import (
    RecomendacaoRequest,
    RecomendacaoResponse,
)
from app.services.embedding_service import embedding_service
from app.api.recommendation_agent.book_recommendation_builder import BookRecommendationBuilder
from app.api.providers.llama_provider import OllamaProvider
from app.api.providers.gemini_provider import GeminiProvider
from app.api.providers.openai_provider import OpenAIProvider
from app.api.utils import Book, BookRecommendationResult

router = APIRouter(prefix="/recomendacoes", tags=["Recomendações"])


@router.post("", response_model=list[RecomendacaoResponse])
async def recomendar_livros(
    payload: RecomendacaoRequest,
    db: AsyncSession = Depends(get_db),
) -> BookRecommendationResult:

    llama_provider = OllamaProvider(model_config={}) 
    gemini_provider = GeminiProvider(model_config={"temperature": 0.3, "token_limit": 300})
    openai_provider = OpenAIProvider(model_config={"temperature": 0.5, "token_limit": 200})

    builder = BookRecommendationBuilder(provider=openai_provider)

    result = await builder.stream_build(
        user_message=payload.preferencia,
        top_k=payload.limite
    )

    return result

    
