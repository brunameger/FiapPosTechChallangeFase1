import pytest
from app import scrapper


def test_coletar_tabela_embrapa_fallback_csv_nao_encontrado():
    with pytest.raises(Exception):
        scrapper.coletar_tabela_embrapa("opcao_inexistente", 2023)


def test_estrutura_resposta_fallback():
    resultado = scrapper._ler_csv_fallback("opt_02", 2023, None)
    assert isinstance(resultado, dict)
    assert "Ano" in resultado
    assert "Dados" in resultado
