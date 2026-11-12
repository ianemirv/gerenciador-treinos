"""Hierarquia 2 — Exercícios: Exercicio (abstrata) e 3 subclasses."""

from abc import ABC, abstractmethod

from models.validacao import inteiro_positivo, numero_positivo, texto_obrigatorio


class Exercicio(ABC):
    """Classe base abstrata. Cada subclasse calcula o volume do seu jeito."""

    def __init__(self, nome, grupo_muscular):
        self.nome = texto_obrigatorio(nome, "nome do exercício")
        self.grupo_muscular = texto_obrigatorio(grupo_muscular, "grupo muscular")

    @abstractmethod
    def calcular_volume(self):
        """Quantidade de trabalho do exercício (POLIMORFISMO)."""

    @abstractmethod
    def descricao(self):
        """Texto curto que descreve o exercício (POLIMORFISMO)."""

    def __str__(self):
        return self.descricao()


class ExercicioMusculacao(Exercicio):
    """Volume = séries × repetições × carga (kg)."""

    def __init__(self, nome, grupo_muscular, series, repeticoes, carga_kg):
        super().__init__(nome, grupo_muscular)
        self.series = inteiro_positivo(series, "séries")
        self.repeticoes = inteiro_positivo(repeticoes, "repetições")
        self.carga_kg = numero_positivo(carga_kg, "carga (kg)", permitir_zero=True)

    def calcular_volume(self):
        return self.series * self.repeticoes * self.carga_kg

    def descricao(self):
        return (f"{self.nome} ({self.grupo_muscular}): "
                f"{self.series}x{self.repeticoes} com {self.carga_kg:g} kg")


class ExercicioCardio(Exercicio):
    """Volume = minutos de atividade."""

    def __init__(self, nome, duracao_min, distancia_km=0, grupo_muscular="Cardio"):
        super().__init__(nome, grupo_muscular)
        self.duracao_min = numero_positivo(duracao_min, "duração (min)")
        self.distancia_km = numero_positivo(distancia_km, "distância (km)", permitir_zero=True)

    def calcular_volume(self):
        return self.duracao_min

    def descricao(self):
        texto = f"{self.nome} ({self.grupo_muscular}): {self.duracao_min:g} min"
        if self.distancia_km > 0:
            texto += f", {self.distancia_km:g} km"
        return texto


class ExercicioIsometrico(Exercicio):
    """Exercício parado, como a prancha. Volume = séries × tempo (s)."""

    def __init__(self, nome, grupo_muscular, series, tempo_s):
        super().__init__(nome, grupo_muscular)
        self.series = inteiro_positivo(series, "séries")
        self.tempo_s = numero_positivo(tempo_s, "tempo (s)")

    def calcular_volume(self):
        return self.series * self.tempo_s

    def descricao(self):
        return (f"{self.nome} ({self.grupo_muscular}): "
                f"{self.series}x{self.tempo_s:g} s")
