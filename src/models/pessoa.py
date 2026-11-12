"""Hierarquia 1 — Pessoas: Pessoa (abstrata), Aluno e Instrutor."""

from abc import ABC, abstractmethod

from models.validacao import inteiro_positivo, numero_positivo, texto_obrigatorio


class Pessoa(ABC):
    """Classe base abstrata. Não pode ser instanciada diretamente."""

    def __init__(self, nome, cpf, idade):
        self.nome = nome
        self.cpf = cpf
        self.idade = idade

    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, valor):
        self._nome = texto_obrigatorio(valor, "nome")

    @property
    def cpf(self):
        return self._cpf

    @cpf.setter
    def cpf(self, valor):
        # Aceita "123.456.789-00" ou "12345678900" e guarda só os dígitos.
        digitos = "".join(c for c in str(valor) if c.isdigit())
        if len(digitos) != 11:
            raise ValueError("O CPF precisa ter 11 dígitos.")
        self._cpf = digitos

    @property
    def idade(self):
        return self._idade

    @idade.setter
    def idade(self, valor):
        self._idade = inteiro_positivo(valor, "idade")

    @abstractmethod
    def apresentar(self):
        """Cada tipo de pessoa se apresenta de um jeito (polimorfismo)."""

    def __str__(self):
        return self.apresentar()


class Aluno(Pessoa):
    """HERANÇA: Aluno é uma Pessoa."""

    def __init__(self, nome, cpf, idade, peso_kg, altura_m):
        super().__init__(nome, cpf, idade)
        self.peso_kg = peso_kg
        self.altura_m = altura_m
        self.fichas = []   # ASSOCIAÇÃO: fichas são criadas fora e ligadas ao aluno
        self.sessoes = []  # ASSOCIAÇÃO: sessões de treino que o aluno fez

    @property
    def peso_kg(self):
        return self._peso_kg

    @peso_kg.setter
    def peso_kg(self, valor):
        self._peso_kg = numero_positivo(valor, "peso (kg)")

    @property
    def altura_m(self):
        return self._altura_m

    @altura_m.setter
    def altura_m(self, valor):
        self._altura_m = numero_positivo(valor, "altura (m)")

    def calcular_imc(self):
        return round(self.peso_kg / self.altura_m ** 2, 2)

    # ---------- fichas ----------
    def buscar_ficha(self, nome_ficha):
        for ficha in self.fichas:
            if ficha.nome.lower() == str(nome_ficha).strip().lower():
                return ficha
        return None

    def adicionar_ficha(self, ficha):
        if self.buscar_ficha(ficha.nome) is not None:
            raise ValueError(f"O aluno já tem uma ficha chamada '{ficha.nome}'.")
        self.fichas.append(ficha)

    def remover_ficha(self, nome_ficha):
        ficha = self.buscar_ficha(nome_ficha)
        if ficha is None:
            raise ValueError(f"Ficha '{nome_ficha}' não encontrada.")
        self.fichas.remove(ficha)

    # ---------- sessões ----------
    def registrar_sessao(self, sessao):
        if sessao.ficha not in self.fichas:
            raise ValueError("A sessão precisa usar uma ficha deste aluno.")
        self.sessoes.append(sessao)

    def apresentar(self):
        return (f"Aluno {self.nome}, {self.idade} anos, "
                f"{self.peso_kg:.1f} kg, IMC {self.calcular_imc():.2f}")


class Instrutor(Pessoa):
    """HERANÇA: Instrutor é uma Pessoa."""

    def __init__(self, nome, cpf, idade, cref):
        super().__init__(nome, cpf, idade)
        self.cref = cref
        self.alunos = []  # ASSOCIAÇÃO: o instrutor acompanha alunos que existem por conta própria

    @property
    def cref(self):
        return self._cref

    @cref.setter
    def cref(self, valor):
        self._cref = texto_obrigatorio(valor, "CREF")

    def buscar_aluno(self, cpf):
        cpf_digitos = "".join(c for c in str(cpf) if c.isdigit())
        for aluno in self.alunos:
            if aluno.cpf == cpf_digitos:
                return aluno
        return None

    def vincular_aluno(self, aluno):
        if not isinstance(aluno, Aluno):
            raise TypeError("Só é possível vincular objetos do tipo Aluno.")
        if self.buscar_aluno(aluno.cpf) is not None:
            raise ValueError(f"{aluno.nome} já está vinculado a este instrutor.")
        self.alunos.append(aluno)

    def desvincular_aluno(self, cpf):
        aluno = self.buscar_aluno(cpf)
        if aluno is None:
            raise ValueError("Aluno não está vinculado a este instrutor.")
        self.alunos.remove(aluno)

    def apresentar(self):
        return (f"Instrutor {self.nome}, CREF {self.cref}, "
                f"acompanha {len(self.alunos)} aluno(s)")
