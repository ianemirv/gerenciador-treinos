"""Testa o menu simulando o que o usuário digita.

O monkeypatch troca o input() por uma lista de respostas prontas.
O fixture "repo" (tests/conftest.py) roda cada teste com o repositório
em memória e com o banco SQLite.
"""

from models.exercicio import ExercicioCardio, ExercicioIsometrico, ExercicioMusculacao
from ui.menu_terminal import MenuTerminal


def rodar_menu(monkeypatch, respostas, repo):
    """Roda o menu com as respostas dadas e devolve o repositório."""
    entradas = iter(respostas)
    monkeypatch.setattr("builtins.input", lambda mensagem="": next(entradas))
    MenuTerminal(repo, pausar=False).executar()
    return repo


CADASTRO_IAN = ["1", "1", "Ian", "555.666.777-88", "19", "72", "1.78", "0"]


def test_sair(monkeypatch, capsys, repo):
    rodar_menu(monkeypatch, ["0"], repo)
    assert "Até o próximo treino" in capsys.readouterr().out


def test_cadastrar_aluno(monkeypatch, repo):
    repo = rodar_menu(monkeypatch, CADASTRO_IAN + ["0"], repo)
    aluno = repo.buscar_aluno("55566677788")
    assert aluno.nome == "Ian"
    assert aluno.calcular_imc() == 22.72


def test_entradas_invalidas_nao_quebram(monkeypatch, capsys, repo):
    respostas = [
        "x", "99",                      # opções inexistentes no menu principal
        "1", "1",
        "",  "Ian",                     # nome vazio
        "123", "555.666.777-88",        # CPF curto
        "-3", "dezenove", "19",         # idade negativa e texto
        "0", "72",                      # peso zero
        "1,78",                         # vírgula também funciona
        "0", "0",
    ]
    repo = rodar_menu(monkeypatch, respostas, repo)
    saida = capsys.readouterr().out
    assert saida.count("✗ Erro") == 7
    assert repo.buscar_aluno("55566677788").altura_m == 1.78


def test_cpf_repetido(monkeypatch, capsys, repo):
    respostas = CADASTRO_IAN[:-1] + ["1", "Outro", "55566677788", "11122233344",
                                     "20", "70", "1.7", "0", "0"]
    repo = rodar_menu(monkeypatch, respostas, repo)
    assert "Já existe uma pessoa cadastrada com esse CPF" in capsys.readouterr().out
    assert len(repo.alunos) == 2


def test_editar_e_excluir_aluno(monkeypatch, repo):
    respostas = CADASTRO_IAN[:-1] + [
        "3", "1", "", "", "75", "",     # editar: só o peso
        "0", "0",
    ]
    repo = rodar_menu(monkeypatch, respostas, repo)
    assert repo.buscar_aluno("55566677788").peso_kg == 75
    rodar_menu(monkeypatch, ["1", "4", "1", "s", "0", "0"], repo)
    assert repo.alunos == []


def test_instrutor_e_vinculo(monkeypatch, capsys, repo):
    respostas = CADASTRO_IAN[:-1] + ["0",
        "2", "1", "Carla", "11122233344", "32", "012345-G/DF",
        "3", "1", "1",                  # vincular Carla -> Ian
        "3", "1", "1",                  # de novo: deve dar erro
        "2",                            # listar
        "0", "0",
    ]
    repo = rodar_menu(monkeypatch, respostas, repo)
    carla = repo.buscar_instrutor("11122233344")
    assert carla.alunos == [repo.buscar_aluno("55566677788")]
    assert "já é acompanhado por Carla" in capsys.readouterr().out


def test_ficha_com_os_tres_tipos_e_sessao(monkeypatch, capsys, repo):
    respostas = CADASTRO_IAN[:-1] + ["0",
        "3", "1", "1", "Treino A", "0",                       # criar ficha
        "4", "1", "1",                                         # exercícios da ficha
        "1", "1", "Supino reto", "Peito", "4", "10", "40",     # musculação
        "1", "2", "Esteira", "20", "3",                        # cardio
        "1", "3", "Prancha", "Abdômen", "3", "45",             # isométrico
        "0",
        "5", "1", "1",                                         # ver ficha
        "6", "1", "1", "11/11/2026", "60", "Bom treino",       # registrar sessão
        "s", "", "8", "42.5",                                  # supino: 4x8 com 42,5
        "s", "",                                               # esteira: minutos planejados
        "n",                                                   # não fez prancha
        "7", "1",                                              # histórico
        "0",
    ]
    repo = rodar_menu(monkeypatch, respostas, repo)
    aluno = repo.buscar_aluno("55566677788")
    ficha = aluno.buscar_ficha("Treino A")
    tipos = [type(e) for e in ficha.exercicios]
    assert tipos == [ExercicioMusculacao, ExercicioCardio, ExercicioIsometrico]

    sessao = aluno.sessoes[0]
    assert [r.descricao() for r in sessao.registros] == [
        "Supino reto: 4x8 com 42.5 kg", "Esteira: 20 min"]
    saida = capsys.readouterr().out
    assert "Volume total: 1755" in saida          # 1600 + 20 + 135
    assert "Volume do dia: 1360 kg" in saida      # 4 x 8 x 42,5


def test_dados_exemplo_e_relatorios(monkeypatch, capsys, repo):
    respostas = [
        "9", "9",                              # carregar 2x: a 2ª avisa que já existe
        "8", "1",                              # relatórios do João
        "1", "1",                              # evolução do supino
        "2",                                   # volume por semana
        "3",                                   # IMC
        "0", "0",
    ]
    repo = rodar_menu(monkeypatch, respostas, repo)
    saida = capsys.readouterr().out
    assert len(repo.alunos) == 2 and len(repo.instrutores) == 1
    assert "já foram carregados" in saida
    assert "Variação desde o primeiro treino: +7.5 kg" in saida
    assert "Semana 45/2026" in saida and "Semana 46/2026" in saida
    assert "IMC: 22.72 — Peso normal" in saida


def test_nao_exclui_ficha_com_sessoes(monkeypatch, capsys, repo):
    repo = rodar_menu(monkeypatch, ["9", "3", "3", "1", "1", "0", "0"], repo)
    assert "não pode ser excluída" in capsys.readouterr().out
    assert repo.buscar_aluno("55566677788").buscar_ficha("Treino A") is not None


def test_opcoes_sem_cadastro_avisam(monkeypatch, capsys, repo):
    rodar_menu(monkeypatch, ["5", "6", "7", "8", "0"], repo)
    assert capsys.readouterr().out.count("Nenhum aluno cadastrado") == 4


def test_remover_exercicio(monkeypatch, repo):
    repo = rodar_menu(monkeypatch, ["9", "4", "1", "1", "2", "4", "0", "0"], repo)
    ficha = repo.buscar_aluno("55566677788").buscar_ficha("Treino A")
    assert ficha.buscar_exercicio("Prancha") is None
