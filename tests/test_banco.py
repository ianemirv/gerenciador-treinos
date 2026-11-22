"""Testes do RepositorioSQLite (nível 3).

A ideia de quase todos: salvar, FECHAR o banco, abrir de novo
e conferir que os dados continuam lá.
"""

import sqlite3
from contextlib import closing
from datetime import date

import pytest

from models.exercicio import ExercicioCardio, ExercicioIsometrico, ExercicioMusculacao
from models.ficha_treino import FichaTreino
from models.pessoa import Aluno, Instrutor
from models.sessao_treino import SessaoTreino
from repository.banco import TABELAS, RepositorioSQLite
from services.relatorio import RelatorioEvolucao
from ui.dados_exemplo import carregar_dados_exemplo
from ui.menu_terminal import MenuTerminal


def contar(caminho, tabela):
    """Quantas linhas a tabela tem (lendo direto do arquivo do banco)."""
    with closing(sqlite3.connect(caminho)) as conexao:
        return conexao.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]


@pytest.fixture
def abertos():
    """Guarda os repositórios abertos no teste para fechar todos no final."""
    lista = []
    yield lista
    for repo in lista:
        repo.fechar()


@pytest.fixture
def banco(caminho_banco, abertos):
    repo = RepositorioSQLite(caminho_banco)
    abertos.append(repo)
    return repo


@pytest.fixture
def reabrir(abertos):
    """Fecha o banco e abre de novo, como se o programa tivesse sido reiniciado."""
    def _reabrir(repo):
        repo.fechar()
        novo = RepositorioSQLite(repo.caminho)
        abertos.append(novo)
        return novo
    return _reabrir


@pytest.fixture
def ian():
    return Aluno("Ian", "555.666.777-88", 19, 72, 1.78)


@pytest.fixture
def carla():
    return Instrutor("Carla", "11122233344", 32, "012345-G/DF")


def ficha_tres_tipos():
    ficha = FichaTreino("Treino A")
    ficha.adicionar_musculacao("Supino reto", "Peito", 4, 10, 40)
    ficha.adicionar_cardio("Esteira", 20, 3)
    ficha.adicionar_isometrico("Prancha", "Abdômen", 3, 45)
    return ficha


# ---------------------------------------------------------------------------
def test_cria_as_seis_tabelas(banco, caminho_banco):
    with closing(sqlite3.connect(caminho_banco)) as conexao:
        nomes = {linha[0] for linha in conexao.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert set(TABELAS) <= nomes


def test_banco_novo_comeca_vazio(banco):
    assert banco.alunos == [] and banco.instrutores == []


def test_aluno_instrutor_e_vinculo_continuam_apos_reabrir(banco, ian, carla, reabrir):
    banco.adicionar_aluno(ian)
    banco.adicionar_instrutor(carla)
    banco.vincular(carla, ian)

    banco = reabrir(banco)
    aluno = banco.buscar_aluno("55566677788")
    assert aluno.nome == "Ian" and aluno.calcular_imc() == 22.72
    assert banco.instrutor_do_aluno(aluno).nome == "Carla"


def test_cpf_continua_unico_apos_reabrir(banco, ian, reabrir):
    banco.adicionar_aluno(ian)
    banco = reabrir(banco)
    with pytest.raises(ValueError):
        banco.adicionar_instrutor(Instrutor("Outro", "55566677788", 30, "123"))


def test_editar_aluno_salva_no_banco(banco, ian, reabrir):
    banco.adicionar_aluno(ian)
    ian.peso_kg = 75
    ian.nome = "Ian Emir"
    banco.atualizar_aluno(ian)

    aluno = reabrir(banco).buscar_aluno(ian.cpf)
    assert aluno.peso_kg == 75 and aluno.nome == "Ian Emir"


def test_desvincular_salva_no_banco(banco, ian, carla, reabrir):
    banco.adicionar_aluno(ian)
    banco.adicionar_instrutor(carla)
    banco.vincular(carla, ian)
    banco.desvincular(carla, ian)

    banco = reabrir(banco)
    assert banco.instrutor_do_aluno(banco.buscar_aluno(ian.cpf)) is None


def test_remover_instrutor_mantem_aluno(banco, ian, carla, reabrir):
    banco.adicionar_aluno(ian)
    banco.adicionar_instrutor(carla)
    banco.vincular(carla, ian)
    banco.remover_instrutor(carla.cpf)

    banco = reabrir(banco)
    assert banco.instrutores == []
    assert banco.instrutor_do_aluno(banco.buscar_aluno(ian.cpf)) is None


def test_ficha_com_os_tres_tipos_volta_igual(banco, ian, reabrir):
    banco.adicionar_aluno(ian)
    banco.adicionar_ficha(ian, ficha_tres_tipos())

    ficha = reabrir(banco).buscar_aluno(ian.cpf).buscar_ficha("Treino A")
    # POLIMORFISMO: cada linha da tabela volta como a classe certa.
    assert [type(e) for e in ficha.exercicios] == [
        ExercicioMusculacao, ExercicioCardio, ExercicioIsometrico]
    assert ficha.calcular_volume_total() == 1600 + 20 + 135
    assert ficha.buscar_exercicio("Esteira").distancia_km == 3


def test_adicionar_e_remover_exercicio(banco, ian, caminho_banco, reabrir):
    banco.adicionar_aluno(ian)
    ficha = FichaTreino("Treino A")
    banco.adicionar_ficha(ian, ficha)
    exercicio = ficha.adicionar_musculacao("Rosca", "Bíceps", 3, 12, 14)
    banco.salvar_exercicio(ficha, exercicio)
    assert contar(caminho_banco, "exercicios") == 1

    banco.remover_exercicio(ficha, exercicio)   # nunca foi usado: sai do banco
    assert contar(caminho_banco, "exercicios") == 0
    assert reabrir(banco).buscar_aluno(ian.cpf).buscar_ficha("Treino A").exercicios == []


def test_sessao_e_registros_continuam_apos_reabrir(banco, ian, reabrir):
    banco.adicionar_aluno(ian)
    ficha = ficha_tres_tipos()
    banco.adicionar_ficha(ian, ficha)
    sessao = SessaoTreino("11/11/2026", ficha, 60, "Bom treino")
    sessao.registrar_exercicio("Supino reto", 4, 8, 42.5)
    sessao.registrar_exercicio("Esteira", 1, 20)
    banco.registrar_sessao(ian, sessao)

    aluno = reabrir(banco).buscar_aluno(ian.cpf)
    sessao = aluno.sessoes[0]
    assert sessao.data == date(2026, 11, 11)
    assert sessao.observacao == "Bom treino"
    assert sessao.ficha is aluno.buscar_ficha("Treino A")   # associação refeita
    assert [r.descricao() for r in sessao.registros] == [
        "Supino reto: 4x8 com 42.5 kg", "Esteira: 20 min"]
    assert sessao.calcular_volume_total() == 1360


def test_exercicio_usado_sai_da_ficha_mas_fica_no_historico(banco, ian, caminho_banco, reabrir):
    banco.adicionar_aluno(ian)
    ficha = ficha_tres_tipos()
    banco.adicionar_ficha(ian, ficha)
    sessao = SessaoTreino("11/11/2026", ficha, 30)
    sessao.registrar_exercicio("Prancha", 3, 45)
    banco.registrar_sessao(ian, sessao)

    banco.remover_exercicio(ficha, ficha.buscar_exercicio("Prancha"))
    assert contar(caminho_banco, "exercicios") == 3   # continua lá, com ativo = 0

    aluno = reabrir(banco).buscar_aluno(ian.cpf)
    assert aluno.buscar_ficha("Treino A").buscar_exercicio("Prancha") is None
    assert aluno.sessoes[0].registros[0].descricao() == "Prancha: 3x45 s"


def test_nao_remove_ficha_com_sessoes(banco, ian):
    banco.adicionar_aluno(ian)
    ficha = ficha_tres_tipos()
    banco.adicionar_ficha(ian, ficha)
    sessao = SessaoTreino("11/11/2026", ficha, 30)
    sessao.registrar_exercicio("Esteira", 1, 20)
    banco.registrar_sessao(ian, sessao)
    with pytest.raises(ValueError):
        banco.remover_ficha(ian, ficha)


def test_remover_ficha_sem_sessoes(banco, ian, caminho_banco):
    banco.adicionar_aluno(ian)
    ficha = ficha_tres_tipos()
    banco.adicionar_ficha(ian, ficha)
    banco.remover_ficha(ian, ficha)
    assert contar(caminho_banco, "fichas") == 0
    assert contar(caminho_banco, "exercicios") == 0   # ON DELETE CASCADE


def test_remover_aluno_apaga_tudo_dele(banco, caminho_banco, reabrir):
    carregar_dados_exemplo(banco)
    banco.remover_aluno("55566677788")   # João: tem fichas, exercícios e sessões

    for tabela, esperado in [("alunos", 1), ("fichas", 1), ("exercicios", 2),
                             ("sessoes", 0), ("registros", 0), ("instrutores", 1)]:
        assert contar(caminho_banco, tabela) == esperado, tabela
    assert reabrir(banco).buscar_aluno("55566677788") is None


def test_dados_de_exemplo_e_relatorio_apos_reabrir(banco, reabrir):
    assert carregar_dados_exemplo(banco) is True
    banco = reabrir(banco)
    assert carregar_dados_exemplo(banco) is False   # não duplica

    joao = banco.buscar_aluno("55566677788")
    assert len(banco.alunos) == 2 and len(joao.fichas) == 2 and len(joao.sessoes) == 7
    relatorio = RelatorioEvolucao()
    assert relatorio.variacao_carga(joao.sessoes, "Supino reto") == 7.5


def test_menu_fechar_e_abrir_de_novo(monkeypatch, caminho_banco):
    """O fluxo do vídeo: cadastra pelo menu, fecha, abre e os dados estão lá."""
    respostas = iter([
        "1", "1", "Ian", "555.666.777-88", "19", "72", "1.78", "0",   # cadastrar aluno
        "3", "1", "1", "Treino A", "0",                                # criar ficha
        "4", "1", "1", "1", "1", "Supino reto", "Peito", "4", "10", "40", "0",
        "6", "1", "1", "11/11/2026", "60", "", "s", "", "", "",       # registrar sessão
        "0",
    ])
    monkeypatch.setattr("builtins.input", lambda mensagem="": next(respostas))
    repo = RepositorioSQLite(caminho_banco)
    MenuTerminal(repo, pausar=False).executar()
    repo.fechar()

    repo = RepositorioSQLite(caminho_banco)   # "abriu o programa de novo"
    aluno = repo.buscar_aluno("55566677788")
    repo.fechar()
    assert aluno.buscar_ficha("Treino A").buscar_exercicio("Supino reto").carga_kg == 40
    assert aluno.sessoes[0].calcular_volume_total() == 1600
