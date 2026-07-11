from typing import Optional

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import settings
from app.db.base import Base


class Livro(Base):
    __tablename__ = "livros"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    titulo: Mapped[Optional[str]] = mapped_column(String(255))
    autor: Mapped[Optional[str]] = mapped_column(String(255))
    genero: Mapped[Optional[str]] = mapped_column(String)
    ano: Mapped[Optional[int]] = mapped_column(Integer)
    numero_paginas: Mapped[Optional[int]] = mapped_column(Integer)
    descricao: Mapped[Optional[str]] = mapped_column(Text)
    embedding: Mapped[Optional[list[float]]] = mapped_column(
        VECTOR(settings.embedding_dimensions)
    )
