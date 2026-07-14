import asyncio

from app.api.recommendation_agent import book_recommendation_builder as builder_module
from app.api.recommendation_agent.book_recommendation_builder import (
    BookRecommendationBuilder,
)
from app.api.utils import Book


class FakeSessionContext:
    async def __aenter__(self):
        return object()

    async def __aexit__(self, exc_type, exc, traceback):
        return False


class EmptyProvider:
    def generate_response_stream(self, prompt: str):
        return iter(())


class ErrorProvider:
    def generate_response_stream(self, prompt: str):
        raise RuntimeError("quota exceeded")


class FakeRagPipeline:
    async def stream_build(self, session, user_query: str, top_k: int):
        return [
            Book(
                title="A Hipótese do Amor",
                author="Ali Hazelwood",
                year=2022,
                number_of_pages=453,
                book_description="Romance acadêmico com namoro falso.",
                category="ROMANCE",
            )
        ]


def build_test_builder(provider):
    builder = BookRecommendationBuilder(provider=provider)
    builder.rag_pipeline = FakeRagPipeline()
    return builder


def test_stream_build_usa_fallback_quando_provider_nao_retorna_tokens(monkeypatch):
    monkeypatch.setattr(
        builder_module,
        "AsyncSessionLocal",
        lambda: FakeSessionContext(),
    )

    result = asyncio.run(
        build_test_builder(EmptyProvider()).stream_build(
            user_message="quero um livro da ali hazelwood",
            top_k=1,
        )
    )

    assert result.response
    assert "A Hipótese do Amor" in result.response
    assert result.retrieved_books[0].title == "A Hipótese do Amor"


def test_stream_build_usa_fallback_quando_provider_lanca_erro(monkeypatch):
    monkeypatch.setattr(
        builder_module,
        "AsyncSessionLocal",
        lambda: FakeSessionContext(),
    )

    result = asyncio.run(
        build_test_builder(ErrorProvider()).stream_build(
            user_message="quero um livro da ali hazelwood",
            top_k=1,
        )
    )

    assert result.response
    assert "A Hipótese do Amor" in result.response
    assert result.retrieved_books[0].title == "A Hipótese do Amor"
