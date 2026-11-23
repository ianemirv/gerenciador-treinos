"""Testes do ControladorGUI (nível 4).

O controlador é a parte da interface gráfica que não usa Tkinter, então
dá para testar sem abrir janelas. Cada teste roda com os dois repositórios
(fixture "repo" do conftest.py).
"""

from datetime import date

import pytest

from models.exercicio import ExercicioCardio, ExercicioIsometrico, ExercicioMusculacao
from repository.banco import RepositorioSQLite
from ui.gui.controlador import ControladorGUI, nome_do_tipo


@pytest.fixture
def ctrl(repo):
    return ControladorGUI(repo)


@pytest.fixture
def aluno(ctrl):
    return ctrl.cadastrar_aluno("Ian", "123.456.789-00", "19", "72", "1,78")


@pytest.fixture
def ficha(ctrl, aluno):
    ficha = ctrl.criar_ficha(aluno, "Treino A")
    ctrl.adicionar_musculacao(ficha, "Supino reto", "Peito", "4", "10", "40")
    ctrl.adicionar_cardio(ficha, "Esteira", "20", "3")
    ctrl.adicionar_isometrico(ficha, "Prancha", "Abdômen", "3", "45")
    return ficha


# ---------------------------------------------------------------- alunos
def test_cadastrar_aluno_com_textos_da_tela(ctrl, aluno):
    assert ctrl.repo.buscar_aluno("12345678900") is aluno
    assert aluno.altura_m == 1.78          # aceita vírgula
    assert ctrl.resumo()["alunos"] == 1


def test_cadastrar_aluno_cpf_repetido(ctrl, aluno):
    with pytest.raises(ValueError, match="CPF"):
        ctrl.cadastrar_aluno("Outro", "12345678900", "20", "70", "1.70")


@pytest.mark.parametrize("campo", ["idade", "peso", "altura"])
def test_cadastrar_aluno_valor_invalido(ctrl, campo):
    dados = {"idade": "19", "peso": "72", "altura": "1.78"}
    dados[campo] = "-3"
    with pytest.raises(ValueError):
        ctrl.cadastrar_aluno("Ian", "12345678900", **dados)
    assert ctrl.repo.alunos == []


def test_editar_aluno(ctrl, aluno):
    ctrl.editar_aluno(aluno, "Ian Emir", "20", "75", "1.78")
    assert (aluno.nome, aluno.idade, aluno.peso_kg) == ("Ian Emir", 20, 75)


def test_editar_aluno_invalido_nao_muda_nada(ctrl, aluno):
    with pytest.raises(ValueError):
        ctrl.editar_aluno(aluno, "Novo nome", "20", "abc", "1.78")
    assert aluno.nome == "Ian" and aluno.idade == 19


def test_excluir_aluno(ctrl, aluno):
    ctrl.excluir_aluno(aluno)
    assert ctrl.repo.alunos == []


# ---------------------------------------------------------------- instrutores
def test_vincular_e_desvincular(ctrl, aluno):
    carla = ctrl.cadastrar_instrutor("Carla", "11122233344", "32", "012345-G/DF")
    assert ctrl.alunos_sem_instrutor() == [aluno]
    ctrl.vincular(carla, aluno)
    assert ctrl.instrutor_do_aluno(aluno) is carla
    assert ctrl.alunos_sem_instrutor() == []
    ctrl.desvincular(carla, aluno)
    assert ctrl.instrutor_do_aluno(aluno) is None


def test_vincular_sem_escolher(ctrl, aluno):
    with pytest.raises(ValueError, match="Escolha"):
        ctrl.vincular(None, aluno)


def test_excluir_instrutor_mantem_alunos(ctrl, aluno):
    carla = ctrl.cadastrar_instrutor("Carla", "11122233344", "32", "012345-G/DF")
    ctrl.vincular(carla, aluno)
    ctrl.excluir_instrutor(carla)
    assert ctrl.repo.instrutores == [] and ctrl.repo.alunos == [aluno]


# ---------------------------------------------------------------- fichas
def test_ficha_com_os_tres_tipos(ficha):
    tipos = [nome_do_tipo(e) for e in ficha.exercicios]
    assert tipos == ["Musculação", "Cardio", "Isométrico"]
    assert ficha.calcular_volume_total() == 1600 + 20 + 135


def test_criar_ficha_sem_aluno(ctrl):
    with pytest.raises(ValueError, match="aluno"):
        ctrl.criar_ficha(None, "Treino A")


def test_criar_ficha_nome_repetido(ctrl, aluno, ficha):
    with pytest.raises(ValueError):
        ctrl.criar_ficha(aluno, "treino a")


def test_cardio_sem_distancia(ctrl, aluno):
    ficha = ctrl.criar_ficha(aluno, "Treino B")
    esteira = ctrl.adicionar_cardio(ficha, "Bicicleta", "15", "")
    assert esteira.distancia_km == 0


def test_exercicio_invalido_nao_entra_na_ficha(ctrl, aluno):
    ficha = ctrl.criar_ficha(aluno, "Treino B")
    with pytest.raises(ValueError):
        ctrl.adicionar_musculacao(ficha, "Supino", "Peito", "0", "10", "40")
    assert ficha.exercicios == []


def test_remover_exercicio_e_excluir_ficha(ctrl, aluno, ficha):
    ctrl.remover_exercicio(ficha, ficha.buscar_exercicio("Esteira"))
    assert len(ficha.exercicios) == 2
    ctrl.excluir_ficha(aluno, ficha)
    assert aluno.fichas == []


# ---------------------------------------------------------------- sessões
def test_campos_registro_por_tipo(ficha):
    supino, esteira, prancha = ficha.exercicios
    assert [c[0] for c in ControladorGUI.campos_registro(supino)] == \
        ["series", "repeticoes", "carga"]
    assert ControladorGUI.campos_registro(esteira) == [("repeticoes", "Minutos", 20)]
    assert [c[2] for c in ControladorGUI.campos_registro(prancha)] == [3, 45]


def test_registrar_sessao(ctrl, aluno, ficha):
    supino, esteira, _ = ficha.exercicios
    feitos = [(supino, {"series": "4", "repeticoes": "10", "carga": "42,5"}),
              (esteira, {"repeticoes": "20"})]
    sessao = ctrl.registrar_sessao(aluno, ficha, "", "60", "Primeiro treino", feitos)
    assert sessao.data == date.today()
    assert len(sessao.registros) == 2
    assert sessao.calcular_volume_total() == 4 * 10 * 42.5
    assert ctrl.historico(aluno) == [sessao]


def test_registrar_sessao_sem_exercicios(ctrl, aluno, ficha):
    with pytest.raises(ValueError, match="pelo menos um"):
        ctrl.registrar_sessao(aluno, ficha, "", "60", "", [])
    assert aluno.sessoes == []


def test_registrar_sessao_valor_invalido_mostra_exercicio(ctrl, aluno, ficha):
    supino = ficha.exercicios[0]
    with pytest.raises(ValueError, match="Supino reto"):
        ctrl.registrar_sessao(aluno, ficha, "", "60", "",
                              [(supino, {"series": "x", "repeticoes": "10", "carga": "40"})])


def test_registrar_sessao_data_invalida(ctrl, aluno, ficha):
    with pytest.raises(ValueError, match="Data"):
        ctrl.registrar_sessao(aluno, ficha, "31/02/2026", "60", "",
                              [(ficha.exercicios[1], {"repeticoes": "20"})])


# ---------------------------------------------------------------- relatórios
def test_relatorios_com_dados_de_exemplo(ctrl):
    assert ctrl.carregar_exemplo() is True
    assert ctrl.carregar_exemplo() is False
    joao = ctrl.repo.buscar_aluno("55566677788")
    assert "Supino reto" in ctrl.exercicios_com_carga(joao)
    evolucao, variacao = ctrl.evolucao_carga(joao, "Supino reto")
    assert evolucao[-1][1] == 47.5 and variacao == 7.5
    assert len(ctrl.volume_por_semana(joao)) == 2
    assert ctrl.imc(joao)[1] == "Peso normal"
    assert ctrl.resumo() == {"alunos": 2, "instrutores": 1, "fichas": 3, "sessoes": 7}


def test_dados_continuam_depois_de_fechar(caminho_banco):
    """O que a interface grava continua no banco ao abrir de novo."""
    repo = RepositorioSQLite(caminho_banco)
    ctrl = ControladorGUI(repo)
    aluno = ctrl.cadastrar_aluno("Ian", "12345678900", "19", "72", "1.78")
    ficha = ctrl.criar_ficha(aluno, "Treino A")
    supino = ctrl.adicionar_musculacao(ficha, "Supino reto", "Peito", "4", "10", "40")
    ctrl.registrar_sessao(aluno, ficha, "20/11/2026", "60", "",
                          [(supino, {"series": "4", "repeticoes": "10", "carga": "42.5"})])
    repo.fechar()

    repo = RepositorioSQLite(caminho_banco)
    aluno = repo.buscar_aluno("12345678900")
    assert isinstance(aluno.fichas[0].exercicios[0], ExercicioMusculacao)
    assert aluno.sessoes[0].registros[0].carga_kg == 42.5
    repo.fechar()


def test_nome_do_tipo():
    assert nome_do_tipo(ExercicioCardio("Esteira", 10)) == "Cardio"
    assert nome_do_tipo(ExercicioIsometrico("Prancha", "Abdômen", 3, 30)) == "Isométrico"
