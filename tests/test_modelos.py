import pytest

from pyticipantes import modelos

NOME = "joão MANOELA da silva santos souza"


@pytest.mark.parametrize(("filtro", "esperado"), [
    ("maiusculo", "JOÃO MANOELA DA SILVA SANTOS SOUZA"),
    ("minusculo", "joão manoela da silva santos souza"),
    ("titulo", "João Manoela da Silva Santos Souza"),
    ("primeiro", "joão"),
    ("ultimo", "souza"),
    ("primeiro_ultimo", "joão souza"),
    ("titulo|abreviar", "João M. S. S. Souza"),
    ("iniciais", "JMSSS"),
])
def test_filtros_de_nome(filtro, esperado):
    assert modelos.substituir(f"{{nome|{filtro}}}", {"nome": NOME}) == esperado


def test_coluna_sem_diferenciar_maiusculas():
    assert modelos.substituir("{NOME}", {"nome": "Ana"}) == "Ana"


def test_marcador_inexistente_permanece():
    assert modelos.substituir("{nada}", {"nome": "Ana"}) == "{nada}"
