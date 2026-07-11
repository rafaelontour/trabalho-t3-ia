from pydantic import BaseModel, ConfigDict


class LivroResponse(BaseModel):
    id: str
    titulo: str | None
    autor: str | None
    genero: str | None
    ano: int | None
    numero_paginas: int | None
    descricao: str | None
    imagem_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class LivroListResponse(BaseModel):
    items: list[LivroResponse]
    total: int
    limite: int
    offset: int
