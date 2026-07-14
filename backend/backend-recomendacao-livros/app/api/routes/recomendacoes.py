from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.recomendacao import (
    RecomendacaoRequest,
    RecomendacaoResultResponse,
)
from app.api.recommendation_agent.book_recommendation_builder import BookRecommendationBuilder
from app.api.providers.openai_provider import OpenAIProvider
from app.api.utils import BookRecommendationResult

router = APIRouter(prefix="/recomendacoes", tags=["Recomendações"])


@router.post("", response_model=RecomendacaoResultResponse)
async def recomendar_livros(
    payload: RecomendacaoRequest,
    db: AsyncSession = Depends(get_db),
) -> BookRecommendationResult:

    openai_provider = OpenAIProvider(model_config={"temperature": 0.5, "token_limit": 200})

    builder = BookRecommendationBuilder(provider=openai_provider)

    result = await builder.stream_build(
        user_message=payload.preferencia,
        top_k=payload.limite
    )

    return result

    
