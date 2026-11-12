"""SessaoTreino e RegistroExercicio: o treino que o aluno realmente fez num dia."""

from datetime import date, datetime

from models.validacao import inteiro_positivo, numero_positivo


class RegistroExercicio:
    """O que foi feito num exercício naquele dia (carga e repetições reais)."""

    def __init__(self, exercicio, series, repeticoes, carga_kg):
        self.exercicio = exercicio  # ASSOCIAÇÃO: aponta para o exercício da ficha
        self.series = inteiro_positivo(series, "séries")
        self.repeticoes = inteiro_positivo(repeticoes, "repetições")
        self.carga_kg = numero_positivo(carga_kg, "carga (kg)", permitir_zero=True)

    def calcular_volume(self):
        return self.series * self.repeticoes * self.carga_kg

    def descricao(self):
        return (f"{self.exercicio.nome}: {self.series}x{self.repeticoes} "
                f"com {self.carga_kg:g} kg")


class SessaoTreino:
    """Um treino feito em uma data.

    ASSOCIAÇÃO com FichaTreino: a sessão aponta para a ficha que foi feita.
    COMPOSIÇÃO com RegistroExercicio: os registros são criados pela sessão
    e não existem sem ela.
    """

    def __init__(self, data, ficha, duracao_min, observacao=""):
        self.data = self._converter_data(data)
        self.ficha = ficha
        self.duracao_min = numero_positivo(duracao_min, "duração (min)")
        self.observacao = str(observacao).strip()
        self._registros = []

    @staticmethod
    def _converter_data(data):
        if isinstance(data, date):
            return data
        try:
            return datetime.strptime(str(data).strip(), "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("Data inválida. Use o formato DD/MM/AAAA.")

    @property
    def registros(self):
        return list(self._registros)

    def registrar_exercicio(self, nome_exercicio, series, repeticoes, carga_kg=0):
        exercicio = self.ficha.buscar_exercicio(nome_exercicio)
        if exercicio is None:
            raise ValueError(f"'{nome_exercicio}' não faz parte da {self.ficha.nome}.")
        registro = RegistroExercicio(exercicio, series, repeticoes, carga_kg)
        self._registros.append(registro)
        return registro

    def calcular_volume_total(self):
        return sum(registro.calcular_volume() for registro in self._registros)

    def resumo(self):
        linhas = [f"{self.data:%d/%m/%Y} - {self.ficha.nome} ({self.duracao_min:g} min)"]
        for registro in self._registros:
            linhas.append(f"  - {registro.descricao()}")
        if self.observacao:
            linhas.append(f"  Obs.: {self.observacao}")
        linhas.append(f"  Volume do dia: {self.calcular_volume_total():g} kg")
        return "\n".join(linhas)

    def __str__(self):
        return self.resumo()
