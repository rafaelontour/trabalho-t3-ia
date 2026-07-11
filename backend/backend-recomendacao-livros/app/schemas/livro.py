from pydantic import BaseModel, ConfigDict


class LivroResponse(BaseModel):
    id: str
    titulo: str | None
    autor: str | None
    genero: str | None
    ano: int | None
    numero_paginas: int | None
    descricao: str | None

    model_config = ConfigDict(from_attributes=True)
