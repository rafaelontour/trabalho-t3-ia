from pydantic import BaseModel, Field, field_validator


class RecomendacaoRequest(BaseModel):
    preferencia: str = Field(
        min_length=3,
        max_length=1000,
        examples=[
            "Gosto de fantasia, magia, aventuras e mundos imaginários."
        ],
    )
    limite: int = Field(default=5, ge=1, le=20)

    @field_validator("preferencia")
    @classmethod
    def validar_preferencia(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("A preferência não pode estar vazia.")
        return value


class RecomendacaoResponse(BaseModel):
    id: str
    titulo: str | None
    autor: str | None
    genero: str | None
    ano: int | None
    numero_paginas: int | None
    descricao: str | None
    imagem_url: str | None = None
    similaridade: float
