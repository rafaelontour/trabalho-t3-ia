from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, livros, recomendacoes
from app.core.config import settings
from app.services.embedding_service import embedding_service


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Carrega o modelo uma única vez durante a inicialização.
    embedding_service.load_model()
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="API de listagem e recomendação semântica de livros.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(livros.router, prefix=settings.api_prefix)
app.include_router(recomendacoes.router, prefix=settings.api_prefix)


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    return {
        "message": settings.app_name,
        "docs": "/docs",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)