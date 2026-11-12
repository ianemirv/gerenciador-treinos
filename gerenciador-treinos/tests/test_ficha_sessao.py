from datetime import date

import pytest

from models.exercicio import ExercicioCardio, ExercicioIsometrico, ExercicioMusculacao
from models.ficha_treino import FichaTreino
from models.pessoa import Aluno
from models.sessao_treino import RegistroExercicio, SessaoTreino


@pytest.fixture
def ficha():
    ficha = FichaTreino("Treino A")
    ficha.adicionar_musculacao("Supino reto", "Peito", 4, 10, 40)
    ficha.adicionar_cardio("Esteira", 30, 5)
    ficha.adicionar_isometrico("Prancha", "Abdômen", 3, 45)
    return ficha


# ---------------- FichaTreino ----------------

def test_ficha_cria_os_exercicios(ficha):
    # Composição: os objetos foram criados pela própria ficha.
    tipos = [type(e) for e in ficha.exercicios]
    assert tipos == [ExercicioMusculacao, ExercicioCardio, ExercicioIsometrico]


def test_volume_total_da_ficha(ficha):
    assert ficha.calcular_volume_total() == 1600 + 30 + 135


def test_ficha_vazia():
    ficha = FichaTreino("Treino B")
    assert ficha.calcular_volume_total() == 0
    assert "nenhum exercício" in ficha.descricao()


def test_remover_exercicio(ficha):
    ficha.remover_exercicio("prancha")
    assert ficha.buscar_exercicio("Prancha") is None
    assert len(ficha.exercicios) == 2
    with pytest.raises(ValueError):
        ficha.remover_exercicio("Agachamento")


def test_nao_aceita_exercicio_repetido(ficha):
    with pytest.raises(ValueError):
        ficha.adicionar_musculacao("Supino Reto", "Peito", 3, 12, 30)


def test_lista_externa_nao_altera_ficha(ficha):
    lista = ficha.exercicios
    lista.clear()
    assert len(ficha.exercicios) == 3


def test_descricao_da_ficha(ficha):
    texto = ficha.descricao()
    assert texto.startswith("Treino A:")
    assert "Supino reto (Peito): 4x10 com 40 kg | volume 1600" in texto
    assert "Volume total: 1765" in texto


def test_nome_da_ficha_vazio():
    with pytest.raises(ValueError):
        FichaTreino("")


# ---------------- SessaoTreino ----------------

def test_data_em_texto_e_convertida(ficha):
    sessao = SessaoTreino("11/11/2026", ficha, 60)
    assert sessao.data == date(2026, 11, 11)


@pytest.mark.parametrize("data", ["2026-11-11", "31/02/2026", ""])
def test_data_invalida(ficha, data):
    with pytest.raises(ValueError):
        SessaoTreino(data, ficha, 60)


def test_registrar_exercicio(ficha):
    sessao = SessaoTreino(date(2026, 11, 11), ficha, 60, "Treino pesado")
    registro = sessao.registrar_exercicio("Supino reto", 4, 8, 45)
    assert isinstance(registro, RegistroExercicio)
    assert registro.exercicio is ficha.buscar_exercicio("Supino reto")
    assert registro.calcular_volume() == 4 * 8 * 45


def test_so_registra_exercicio_da_ficha(ficha):
    sessao = SessaoTreino(date(2026, 11, 11), ficha, 60)
    with pytest.raises(ValueError):
        sessao.registrar_exercicio("Agachamento", 4, 10, 60)


def test_volume_total_da_sessao(ficha):
    sessao = SessaoTreino(date(2026, 11, 11), ficha, 60)
    sessao.registrar_exercicio("Supino reto", 4, 10, 40)
    sessao.registrar_exercicio("Prancha", 3, 1)  # sem carga
    assert sessao.calcular_volume_total() == 1600


def test_resumo_da_sessao(ficha):
    sessao = SessaoTreino(date(2026, 11, 11), ficha, 55, "Bom treino")
    sessao.registrar_exercicio("Supino reto", 4, 10, 40)
    texto = sessao.resumo()
    assert texto.startswith("11/11/2026 - Treino A (55 min)")
    assert "Obs.: Bom treino" in texto


def test_aluno_registra_sessao_da_propria_ficha(ficha):
    aluno = Aluno("Ian", "55566677788", 19, 72, 1.78)
    aluno.adicionar_ficha(ficha)
    sessao = SessaoTreino(date(2026, 11, 11), ficha, 60)
    aluno.registrar_sessao(sessao)
    assert aluno.sessoes == [sessao]


def test_aluno_nao_registra_sessao_de_ficha_alheia(ficha):
    aluno = Aluno("Ian", "55566677788", 19, 72, 1.78)
    sessao = SessaoTreino(date(2026, 11, 11), ficha, 60)
    with pytest.raises(ValueError):
        aluno.registrar_sessao(sessao)
