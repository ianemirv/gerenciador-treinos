from datetime import date

import pytest

from models.ficha_treino import FichaTreino
from models.pessoa import Aluno
from models.sessao_treino import SessaoTreino
from services.relatorio import RelatorioEvolucao


@pytest.fixture
def relatorio():
    return RelatorioEvolucao()


@pytest.fixture
def sessoes():
    ficha = FichaTreino("Treino A")
    ficha.adicionar_musculacao("Supino reto", "Peito", 4, 10, 40)
    ficha.adicionar_musculacao("Rosca direta", "Bíceps", 3, 12, 10)

    def nova(dia, carga_supino):
        sessao = SessaoTreino(date(2026, 11, dia), ficha, 60)
        sessao.registrar_exercicio("Supino reto", 4, 10, carga_supino)
        return sessao

    # Fora de ordem de propósito: o relatório tem que ordenar pela data.
    s3 = nova(10, 45)
    s1 = nova(2, 40)
    s2 = nova(5, 42.5)
    s2.registrar_exercicio("Supino reto", 1, 5, 50)  # série extra mais pesada
    s2.registrar_exercicio("Rosca direta", 3, 12, 12)
    return [s3, s1, s2]


def test_relatorio_nao_guarda_sessoes(relatorio):
    # Dependência: o relatório não tem atributos, só usa o que recebe.
    assert vars(relatorio) == {}


def test_evolucao_carga(relatorio, sessoes):
    assert relatorio.evolucao_carga(sessoes, "supino reto") == [
        (date(2026, 11, 2), 40),
        (date(2026, 11, 5), 50),  # maior carga do dia
        (date(2026, 11, 10), 45),
    ]


def test_evolucao_de_exercicio_feito_uma_vez(relatorio, sessoes):
    assert relatorio.evolucao_carga(sessoes, "Rosca direta") == [(date(2026, 11, 5), 12)]
    assert relatorio.variacao_carga(sessoes, "Rosca direta") == 0.0


def test_variacao_carga(relatorio, sessoes):
    assert relatorio.variacao_carga(sessoes, "Supino reto") == 5


def test_sem_sessoes(relatorio):
    assert relatorio.evolucao_carga([], "Supino reto") == []
    assert relatorio.volume_por_semana([]) == {}


def test_volume_por_semana(relatorio, sessoes):
    # 02/11 e 05/11 são da semana 45; 10/11 é da semana 46.
    assert relatorio.volume_por_semana(sessoes) == {
        "Semana 45/2026": 1600 + (1700 + 250 + 432),
        "Semana 46/2026": 1800,
    }


@pytest.mark.parametrize("peso, faixa", [
    (55, "Abaixo do peso"),
    (70, "Peso normal"),
    (85, "Sobrepeso"),
    (100, "Obesidade"),
])
def test_classificar_imc(relatorio, peso, faixa):
    aluno = Aluno("Ian", "55566677788", 19, peso, 1.78)
    imc, resultado = relatorio.classificar_imc(aluno)
    assert imc == aluno.calcular_imc()
    assert resultado == faixa
