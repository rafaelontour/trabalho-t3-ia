from threading import Lock

from sentence_transformers import SentenceTransformer

from app.core.config import settings


class EmbeddingService:
    def __init__(self) -> None:
        self._model: SentenceTransformer | None = None
        self._lock = Lock()

    def load_model(self) -> SentenceTransformer:
        if self._model is None:
            with self._lock:
                if self._model is None:
                    self._model = SentenceTransformer(
                        settings.embedding_model
                    )
        return self._model

    def gerar_embedding(self, texto: str) -> list[float]:
        texto = texto.strip()
        if not texto:
            raise ValueError("O texto não pode estar vazio.")

        model = self.load_model()
        vetor = model.encode(
            texto,
            normalize_embeddings=True,
        )

        embedding = vetor.tolist()

        if len(embedding) != settings.embedding_dimensions:
            raise RuntimeError(
                "O modelo gerou um vetor com dimensão diferente da coluna "
                f"VECTOR({settings.embedding_dimensions})."
            )

        return embedding


embedding_service = EmbeddingService()
