"""Dados de exemplo para demonstrar o menu sem digitar tudo do zero."""

from models.ficha_treino import FichaTreino
from models.pessoa import Aluno, Instrutor
from models.sessao_treino import SessaoTreino

CPF_INSTRUTOR = "11122233344"


def carregar_dados_exemplo(repositorio):
    """Cria 1 instrutor, 2 alunos, fichas e sessões. Devolve False se já existirem."""
    if repositorio.cpf_em_uso(CPF_INSTRUTOR):
        return False

    carla = Instrutor("Carla Souza", CPF_INSTRUTOR, 32, "012345-G/DF")
    joao = Aluno("João Silva", "55566677788", 20, 72, 1.78)
    maria = Aluno("Maria Oliveira", "22233344455", 25, 60, 1.65)
    repositorio.adicionar_instrutor(carla)
    repositorio.adicionar_aluno(joao)
    repositorio.adicionar_aluno(maria)
    repositorio.vincular(carla, joao)   # Maria fica sem instrutor para dar para vincular no menu

    treino_a = FichaTreino("Treino A")
    treino_a.adicionar_musculacao("Supino reto", "Peito", 4, 10, 40)
    treino_a.adicionar_musculacao("Tríceps corda", "Tríceps", 3, 12, 20)
    treino_a.adicionar_cardio("Esteira", 20, 3)
    treino_a.adicionar_isometrico("Prancha", "Abdômen", 3, 45)
    joao.adicionar_ficha(treino_a)

    treino_b = FichaTreino("Treino B")
    treino_b.adicionar_musculacao("Agachamento", "Pernas", 4, 10, 60)
    treino_b.adicionar_musculacao("Leg press", "Pernas", 4, 12, 120)
    treino_b.adicionar_cardio("Bicicleta", 15)
    joao.adicionar_ficha(treino_b)

    # (data, ficha, carga do exercício principal) — a carga sobe ao longo das semanas
    historico = [
        ("03/11/2026", treino_a, 40), ("04/11/2026", treino_b, 60),
        ("06/11/2026", treino_a, 42.5), ("07/11/2026", treino_b, 65),
        ("10/11/2026", treino_a, 45), ("11/11/2026", treino_b, 70),
        ("13/11/2026", treino_a, 47.5),
    ]
    for data, ficha, carga in historico:
        sessao = SessaoTreino(data, ficha, 60)
        if ficha is treino_a:
            sessao.registrar_exercicio("Supino reto", 4, 10, carga)
            sessao.registrar_exercicio("Tríceps corda", 3, 12, 20)
            sessao.registrar_exercicio("Esteira", 1, 20)
            sessao.registrar_exercicio("Prancha", 3, 45)
        else:
            sessao.registrar_exercicio("Agachamento", 4, 10, carga)
            sessao.registrar_exercicio("Leg press", 4, 12, 120)
            sessao.registrar_exercicio("Bicicleta", 1, 15)
        joao.registrar_sessao(sessao)

    treino_maria = FichaTreino("Treino A")
    treino_maria.adicionar_musculacao("Cadeira extensora", "Quadríceps", 3, 12, 25)
    treino_maria.adicionar_cardio("Elíptico", 25, 4)
    maria.adicionar_ficha(treino_maria)
    return True
