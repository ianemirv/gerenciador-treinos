"""Demonstração do nível 1: cria objetos e mostra todas as classes funcionando.

Rode com:  python src/main.py
(No nível 2 este arquivo vai abrir o menu do terminal.)
"""

from models.ficha_treino import FichaTreino
from models.pessoa import Aluno, Instrutor
from models.sessao_treino import SessaoTreino
from services.relatorio import RelatorioEvolucao


def titulo(texto):
    print(f"\n=== {texto} ===")


def main():
    titulo("Pessoas (herança + polimorfismo em apresentar)")
    instrutor = Instrutor("Carla Souza", "111.222.333-44", 32, "012345-G/DF")
    aluno = Aluno("Ian", "555.666.777-88", 19, 72, 1.78)
    instrutor.vincular_aluno(aluno)  # associação
    for pessoa in (instrutor, aluno):
        print(pessoa.apresentar())

    titulo("Ficha de treino (composição + polimorfismo no volume)")
    ficha_a = FichaTreino("Treino A")
    ficha_a.adicionar_musculacao("Supino reto", "Peito", 4, 10, 40)
    ficha_a.adicionar_cardio("Esteira", 20, 3)
    ficha_a.adicionar_isometrico("Prancha", "Abdômen", 3, 45)
    aluno.adicionar_ficha(ficha_a)  # associação
    print(ficha_a.descricao())

    titulo("Sessões de treino (composição de registros)")
    datas_cargas = [("02/11/2026", 40), ("05/11/2026", 42.5), ("10/11/2026", 45)]
    for data, carga in datas_cargas:
        sessao = SessaoTreino(data, ficha_a, 60)
        sessao.registrar_exercicio("Supino reto", 4, 10, carga)
        aluno.registrar_sessao(sessao)
    for sessao in aluno.sessoes:
        print(sessao.resumo())

    titulo("Relatório de evolução (dependência)")
    relatorio = RelatorioEvolucao()
    for data, carga in relatorio.evolucao_carga(aluno.sessoes, "Supino reto"):
        print(f"{data:%d/%m/%Y}: {carga:g} kg")
    print(f"Variação: +{relatorio.variacao_carga(aluno.sessoes, 'Supino reto'):g} kg")
    for semana, volume in relatorio.volume_por_semana(aluno.sessoes).items():
        print(f"{semana}: volume {volume:g} kg")
    imc, faixa = relatorio.classificar_imc(aluno)
    print(f"IMC de {aluno.nome}: {imc:.2f} ({faixa})")


if __name__ == "__main__":
    main()
