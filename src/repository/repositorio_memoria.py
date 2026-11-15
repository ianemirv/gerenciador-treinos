"""RepositorioMemoria: guarda alunos e instrutores enquanto o programa roda.

Nível 2: os dados ficam só na memória (listas) e somem ao fechar o programa.
No nível 3 vai existir um Repositorio com SQLite com os mesmos métodos,
assim o menu não precisa mudar.
"""

from models.pessoa import Aluno, Instrutor


def so_digitos(cpf):
    return "".join(c for c in str(cpf) if c.isdigit())


class RepositorioMemoria:

    def __init__(self):
        self._alunos = []
        self._instrutores = []

    @property
    def alunos(self):
        return list(self._alunos)

    @property
    def instrutores(self):
        return list(self._instrutores)

    # ---------- CPF ----------
    def cpf_em_uso(self, cpf):
        """Um CPF não pode se repetir, nem entre alunos e instrutores."""
        return self.buscar_aluno(cpf) is not None or self.buscar_instrutor(cpf) is not None

    def _verificar_cpf_livre(self, pessoa):
        if self.cpf_em_uso(pessoa.cpf):
            raise ValueError("Já existe uma pessoa cadastrada com esse CPF.")

    # ---------- alunos ----------
    def adicionar_aluno(self, aluno):
        if not isinstance(aluno, Aluno):
            raise TypeError("Só é possível adicionar objetos do tipo Aluno.")
        self._verificar_cpf_livre(aluno)
        self._alunos.append(aluno)

    def buscar_aluno(self, cpf):
        cpf = so_digitos(cpf)
        for aluno in self._alunos:
            if aluno.cpf == cpf:
                return aluno
        return None

    def remover_aluno(self, cpf):
        aluno = self.buscar_aluno(cpf)
        if aluno is None:
            raise ValueError("Aluno não encontrado.")
        # O aluno também sai da lista do instrutor que o acompanhava.
        instrutor = self.instrutor_do_aluno(aluno)
        if instrutor is not None:
            instrutor.desvincular_aluno(aluno.cpf)
        self._alunos.remove(aluno)

    # ---------- instrutores ----------
    def adicionar_instrutor(self, instrutor):
        if not isinstance(instrutor, Instrutor):
            raise TypeError("Só é possível adicionar objetos do tipo Instrutor.")
        self._verificar_cpf_livre(instrutor)
        self._instrutores.append(instrutor)

    def buscar_instrutor(self, cpf):
        cpf = so_digitos(cpf)
        for instrutor in self._instrutores:
            if instrutor.cpf == cpf:
                return instrutor
        return None

    def remover_instrutor(self, cpf):
        instrutor = self.buscar_instrutor(cpf)
        if instrutor is None:
            raise ValueError("Instrutor não encontrado.")
        # Associação: os alunos continuam existindo sem o instrutor.
        self._instrutores.remove(instrutor)

    def instrutor_do_aluno(self, aluno):
        """Cada aluno é acompanhado por no máximo um instrutor."""
        for instrutor in self._instrutores:
            if instrutor.buscar_aluno(aluno.cpf) is not None:
                return instrutor
        return None

    def vincular(self, instrutor, aluno):
        atual = self.instrutor_do_aluno(aluno)
        if atual is not None:
            raise ValueError(f"{aluno.nome} já é acompanhado por {atual.nome}.")
        instrutor.vincular_aluno(aluno)
