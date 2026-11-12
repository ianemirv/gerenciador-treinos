import pytest

from models.ficha_treino import FichaTreino
from models.pessoa import Aluno, Instrutor, Pessoa


@pytest.fixture
def aluno():
    return Aluno("Ian", "555.666.777-88", 19, 80, 1.80)


@pytest.fixture
def instrutor():
    return Instrutor("Carla", "11122233344", 32, "012345-G/DF")


def test_pessoa_e_abstrata():
    with pytest.raises(TypeError):
        Pessoa("Alguém", "11122233344", 20)


def test_heranca(aluno, instrutor):
    assert isinstance(aluno, Pessoa)
    assert isinstance(instrutor, Pessoa)


def test_calcular_imc(aluno):
    assert aluno.calcular_imc() == 24.69


def test_cpf_guarda_so_digitos(aluno):
    assert aluno.cpf == "55566677788"


@pytest.mark.parametrize("cpf", ["123", "abc", "123.456.789-0"])
def test_cpf_invalido(cpf):
    with pytest.raises(ValueError):
        Aluno("Ian", cpf, 19, 80, 1.8)


@pytest.mark.parametrize("campo, valor", [
    ("nome", ""), ("idade", -3), ("peso_kg", 0), ("altura_m", "alto"),
])
def test_dados_invalidos_do_aluno(campo, valor):
    dados = {"nome": "Ian", "cpf": "55566677788", "idade": 19,
             "peso_kg": 80, "altura_m": 1.8}
    dados[campo] = valor
    with pytest.raises(ValueError):
        Aluno(**dados)


def test_editar_aluno(aluno):
    aluno.peso_kg = 75
    assert aluno.peso_kg == 75
    with pytest.raises(ValueError):
        aluno.idade = 0
    assert aluno.idade == 19  # valor antigo continua


def test_polimorfismo_apresentar(aluno, instrutor):
    textos = [p.apresentar() for p in (aluno, instrutor)]
    assert textos[0].startswith("Aluno Ian")
    assert textos[1].startswith("Instrutor Carla")
    assert str(aluno) == aluno.apresentar()


def test_vincular_e_desvincular_aluno(aluno, instrutor):
    instrutor.vincular_aluno(aluno)
    assert instrutor.alunos == [aluno]
    assert instrutor.buscar_aluno("555.666.777-88") is aluno
    instrutor.desvincular_aluno(aluno.cpf)
    assert instrutor.alunos == []


def test_aluno_continua_existindo_sem_instrutor(aluno, instrutor):
    # Associação: o aluno não depende do instrutor para existir.
    instrutor.vincular_aluno(aluno)
    del instrutor
    assert aluno.nome == "Ian"


def test_nao_vincula_aluno_repetido(aluno, instrutor):
    instrutor.vincular_aluno(aluno)
    with pytest.raises(ValueError):
        instrutor.vincular_aluno(aluno)


def test_so_vincula_aluno(instrutor):
    with pytest.raises(TypeError):
        instrutor.vincular_aluno("Ian")


def test_desvincular_inexistente(instrutor):
    with pytest.raises(ValueError):
        instrutor.desvincular_aluno("99988877766")


def test_fichas_do_aluno(aluno):
    aluno.adicionar_ficha(FichaTreino("Treino A"))
    aluno.adicionar_ficha(FichaTreino("Treino B"))
    assert [f.nome for f in aluno.fichas] == ["Treino A", "Treino B"]
    with pytest.raises(ValueError):
        aluno.adicionar_ficha(FichaTreino("treino a"))  # nome repetido
    aluno.remover_ficha("Treino A")
    assert aluno.buscar_ficha("Treino A") is None
    with pytest.raises(ValueError):
        aluno.remover_ficha("Treino Z")
