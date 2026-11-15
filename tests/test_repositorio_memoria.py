import pytest

from models.pessoa import Aluno, Instrutor
from repository.repositorio_memoria import RepositorioMemoria


@pytest.fixture
def repo():
    return RepositorioMemoria()


@pytest.fixture
def aluno():
    return Aluno("Ian", "555.666.777-88", 19, 72, 1.78)


@pytest.fixture
def instrutor():
    return Instrutor("Carla", "11122233344", 32, "012345-G/DF")


def test_adicionar_e_buscar_aluno(repo, aluno):
    repo.adicionar_aluno(aluno)
    assert repo.buscar_aluno("55566677788") is aluno
    assert repo.alunos == [aluno]


def test_cpf_nao_pode_repetir(repo, aluno, instrutor):
    repo.adicionar_aluno(aluno)
    with pytest.raises(ValueError):
        repo.adicionar_aluno(Aluno("Outro", "55566677788", 20, 70, 1.7))
    # Nem entre aluno e instrutor
    with pytest.raises(ValueError):
        repo.adicionar_instrutor(Instrutor("Outro", "55566677788", 30, "123"))


def test_so_aceita_o_tipo_certo(repo, aluno, instrutor):
    with pytest.raises(TypeError):
        repo.adicionar_aluno(instrutor)
    with pytest.raises(TypeError):
        repo.adicionar_instrutor(aluno)


def test_lista_externa_nao_altera_repositorio(repo, aluno):
    repo.adicionar_aluno(aluno)
    repo.alunos.clear()
    assert len(repo.alunos) == 1


def test_remover_aluno_tambem_desvincula(repo, aluno, instrutor):
    repo.adicionar_aluno(aluno)
    repo.adicionar_instrutor(instrutor)
    repo.vincular(instrutor, aluno)
    repo.remover_aluno(aluno.cpf)
    assert repo.alunos == []
    assert instrutor.alunos == []
    with pytest.raises(ValueError):
        repo.remover_aluno(aluno.cpf)


def test_remover_instrutor_mantem_alunos(repo, aluno, instrutor):
    repo.adicionar_aluno(aluno)
    repo.adicionar_instrutor(instrutor)
    repo.vincular(instrutor, aluno)
    repo.remover_instrutor(instrutor.cpf)
    assert repo.instrutores == []
    assert repo.alunos == [aluno]
    assert repo.instrutor_do_aluno(aluno) is None


def test_aluno_tem_no_maximo_um_instrutor(repo, aluno, instrutor):
    outro = Instrutor("Bruno", "99988877766", 40, "999999-G/DF")
    for pessoa in (aluno, instrutor, outro):
        if isinstance(pessoa, Aluno):
            repo.adicionar_aluno(pessoa)
        else:
            repo.adicionar_instrutor(pessoa)
    repo.vincular(instrutor, aluno)
    assert repo.instrutor_do_aluno(aluno) is instrutor
    with pytest.raises(ValueError):
        repo.vincular(outro, aluno)
