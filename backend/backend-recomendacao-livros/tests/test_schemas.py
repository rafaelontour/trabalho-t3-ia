import pytest
from pydantic import ValidationError

from app.schemas.recomendacao import RecomendacaoRequest


def test_recomendacao_valida():
    payload = RecomendacaoRequest(
        preferencia="Gosto de fantasia e aventura.",
        limite=5,
    )

    assert payload.limite == 5


def test_recomendacao_rejeita_texto_vazio():
    with pytest.raises(ValidationError):
        RecomendacaoRequest(preferencia="   ")
