"""FichaTreino: um treino (A, B, C...) com sua lista de exercícios."""

from models.exercicio import ExercicioCardio, ExercicioIsometrico, ExercicioMusculacao
from models.validacao import texto_obrigatorio


class FichaTreino:
    """COMPOSIÇÃO: a ficha cria e guarda seus próprios exercícios.

    Os exercícios nascem dentro da ficha (pelos métodos adicionar_*) e
    só existem enquanto a ficha existe.
    """

    def __init__(self, nome):
        self.nome = texto_obrigatorio(nome, "nome da ficha")
        self._exercicios = []

    @property
    def exercicios(self):
        # Devolve uma cópia: quem está fora não consegue mexer na lista interna.
        return list(self._exercicios)

    def _verificar_nome_livre(self, nome):
        if self.buscar_exercicio(nome) is not None:
            raise ValueError(f"A ficha já tem um exercício chamado '{nome}'.")

    def adicionar_musculacao(self, nome, grupo_muscular, series, repeticoes, carga_kg):
        self._verificar_nome_livre(nome)
        exercicio = ExercicioMusculacao(nome, grupo_muscular, series, repeticoes, carga_kg)
        self._exercicios.append(exercicio)
        return exercicio

    def adicionar_cardio(self, nome, duracao_min, distancia_km=0):
        self._verificar_nome_livre(nome)
        exercicio = ExercicioCardio(nome, duracao_min, distancia_km)
        self._exercicios.append(exercicio)
        return exercicio

    def adicionar_isometrico(self, nome, grupo_muscular, series, tempo_s):
        self._verificar_nome_livre(nome)
        exercicio = ExercicioIsometrico(nome, grupo_muscular, series, tempo_s)
        self._exercicios.append(exercicio)
        return exercicio

    def buscar_exercicio(self, nome):
        for exercicio in self._exercicios:
            if exercicio.nome.lower() == str(nome).strip().lower():
                return exercicio
        return None

    def remover_exercicio(self, nome):
        exercicio = self.buscar_exercicio(nome)
        if exercicio is None:
            raise ValueError(f"Exercício '{nome}' não encontrado na ficha.")
        self._exercicios.remove(exercicio)

    def calcular_volume_total(self):
        # POLIMORFISMO: cada exercício calcula o próprio volume,
        # a ficha não precisa saber de que tipo ele é.
        return sum(exercicio.calcular_volume() for exercicio in self._exercicios)

    def descricao(self):
        linhas = [f"{self.nome}:"]
        if not self._exercicios:
            linhas.append("  (nenhum exercício)")
        for exercicio in self._exercicios:
            linhas.append(f"  - {exercicio.descricao()} | volume {exercicio.calcular_volume():g}")
        linhas.append(f"  Volume total: {self.calcular_volume_total():g}")
        return "\n".join(linhas)

    def __str__(self):
        return self.descricao()
