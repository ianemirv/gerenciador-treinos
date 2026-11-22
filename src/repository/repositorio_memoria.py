"""RepositorioMemoria: guarda alunos e instrutores enquanto o programa roda.

Nível 2: os dados ficam só na memória (listas) e somem ao fechar o programa.
Nível 3: o RepositorioSQLite (repository/banco.py) HERDA desta classe e, em cada
método que altera os dados, chama a versão daqui (super()) e depois grava no banco.

Por isso toda alteração feita pelo menu passa por um método do repositório
(adicionar, atualizar, remover...). Assim o menu funciona igual com os dois
repositórios (POLIMORFISMO).
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

    def descricao(self):
        """Onde os dados ficam guardados (mostrado ao sair do programa)."""
        return "Os dados ficaram só na memória e foram apagados."

    def fechar(self):
        """Na memória não há nada para fechar."""

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

    def atualizar_aluno(self, aluno):
        """Chamado depois de editar nome, idade, peso ou altura.

        Na memória o próprio objeto já foi alterado, então não há nada a fazer.
        """
        if aluno not in self._alunos:
            raise ValueError("Aluno não encontrado.")

    def remover_aluno(self, cpf):
        aluno = self.buscar_aluno(cpf)
        if aluno is None:
            raise ValueError("Aluno não encontrado.")
        # O aluno também sai da lista do instrutor que o acompanhava.
        instrutor = self.instrutor_do_aluno(aluno)
        if instrutor is not None:
            instrutor.desvincular_aluno(aluno.cpf)
        self._alunos.remove(aluno)
        return aluno

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
        return instrutor

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

    def desvincular(self, instrutor, aluno):
        instrutor.desvincular_aluno(aluno.cpf)

    # ---------- fichas ----------
    def adicionar_ficha(self, aluno, ficha):
        """Liga a ficha ao aluno (com os exercícios que ela já tiver)."""
        aluno.adicionar_ficha(ficha)

    def remover_ficha(self, aluno, ficha):
        if any(sessao.ficha is ficha for sessao in aluno.sessoes):
            raise ValueError("Essa ficha já tem sessões registradas e não pode ser excluída.")
        aluno.remover_ficha(ficha.nome)

    # ---------- exercícios ----------
    def salvar_exercicio(self, ficha, exercicio):
        """Chamado logo depois de a ficha criar um exercício novo.

        COMPOSIÇÃO: quem cria o exercício é a ficha (ficha.adicionar_*).
        Na memória ele já está dentro da ficha, então não há nada a fazer.
        """
        if exercicio not in ficha.exercicios:
            raise ValueError("O exercício precisa ser criado pela ficha.")

    def remover_exercicio(self, ficha, exercicio):
        ficha.remover_exercicio(exercicio.nome)

    # ---------- sessões ----------
    def registrar_sessao(self, aluno, sessao):
        aluno.registrar_sessao(sessao)
