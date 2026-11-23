"""ControladorGUI: a parte da interface gráfica que NÃO depende do Tkinter.

As telas pegam o que o usuário digitou (sempre texto) e chamam um método
daqui. O controlador valida, cria os objetos do modelo e chama o repositório.
Se algo estiver errado, ele lança ValueError e a tela mostra a mensagem numa
janela de erro.

Vantagens de separar assim:
- as telas ficam só com o visual (campos, botões, tabelas);
- dá para testar toda a lógica com pytest, sem abrir janelas
  (tests/test_controlador_gui.py), com os dois repositórios.

Igual ao menu do terminal, TODA alteração passa por um método do repositório.
"""

from datetime import date

from models.exercicio import ExercicioCardio, ExercicioIsometrico, ExercicioMusculacao
from models.ficha_treino import FichaTreino
from models.pessoa import Aluno, Instrutor
from models.sessao_treino import SessaoTreino
from models.validacao import inteiro_positivo, numero_positivo, texto_obrigatorio
from services.relatorio import RelatorioEvolucao
from ui.dados_exemplo import carregar_dados_exemplo
from ui.menu_terminal import formatar_cpf  # noqa: F401 (as telas usam daqui)

# Nome que aparece na tela para cada subclasse de Exercicio.
NOMES_TIPOS = {
    ExercicioMusculacao: "Musculação",
    ExercicioCardio: "Cardio",
    ExercicioIsometrico: "Isométrico",
}


def nome_do_tipo(exercicio):
    return NOMES_TIPOS.get(type(exercicio), "Exercício")


class ControladorGUI:

    def __init__(self, repositorio):
        self.repo = repositorio            # RepositorioSQLite (ou RepositorioMemoria nos testes)
        self.relatorio = RelatorioEvolucao()

    # =====================================================================
    # Início
    # =====================================================================
    def resumo(self):
        """Números mostrados nos cartões da tela inicial."""
        alunos = self.repo.alunos
        return {
            "alunos": len(alunos),
            "instrutores": len(self.repo.instrutores),
            "fichas": sum(len(aluno.fichas) for aluno in alunos),
            "sessoes": sum(len(aluno.sessoes) for aluno in alunos),
        }

    def carregar_exemplo(self):
        """Devolve False se os dados de exemplo já tiverem sido carregados."""
        return carregar_dados_exemplo(self.repo)

    # =====================================================================
    # Alunos
    # =====================================================================
    def cadastrar_aluno(self, nome, cpf, idade, peso, altura):
        # O construtor do Aluno valida cada campo (setters).
        aluno = Aluno(nome, cpf, idade, peso, altura)
        self.repo.adicionar_aluno(aluno)   # valida CPF repetido e salva
        return aluno

    def editar_aluno(self, aluno, nome, idade, peso, altura):
        # Valida TUDO antes de mexer no objeto: se um campo estiver errado,
        # o aluno continua exatamente como estava.
        nome = texto_obrigatorio(nome, "nome")
        idade = inteiro_positivo(idade, "idade")
        peso = numero_positivo(peso, "peso (kg)")
        altura = numero_positivo(altura, "altura (m)")
        aluno.nome, aluno.idade, aluno.peso_kg, aluno.altura_m = nome, idade, peso, altura
        self.repo.atualizar_aluno(aluno)   # UPDATE no banco
        return aluno

    def excluir_aluno(self, aluno):
        self.repo.remover_aluno(aluno.cpf)

    def instrutor_do_aluno(self, aluno):
        return self.repo.instrutor_do_aluno(aluno)

    # =====================================================================
    # Instrutores
    # =====================================================================
    def cadastrar_instrutor(self, nome, cpf, idade, cref):
        instrutor = Instrutor(nome, cpf, idade, cref)
        self.repo.adicionar_instrutor(instrutor)
        return instrutor

    def excluir_instrutor(self, instrutor):
        self.repo.remover_instrutor(instrutor.cpf)

    def alunos_sem_instrutor(self):
        return [aluno for aluno in self.repo.alunos
                if self.repo.instrutor_do_aluno(aluno) is None]

    def vincular(self, instrutor, aluno):
        if instrutor is None or aluno is None:
            raise ValueError("Escolha o instrutor e o aluno.")
        self.repo.vincular(instrutor, aluno)

    def desvincular(self, instrutor, aluno):
        self.repo.desvincular(instrutor, aluno)

    # =====================================================================
    # Fichas e exercícios
    # =====================================================================
    def criar_ficha(self, aluno, nome):
        if aluno is None:
            raise ValueError("Escolha um aluno primeiro.")
        ficha = FichaTreino(nome)
        self.repo.adicionar_ficha(aluno, ficha)   # erro se o aluno já tiver esse nome
        return ficha

    def excluir_ficha(self, aluno, ficha):
        self.repo.remover_ficha(aluno, ficha)     # erro se a ficha já tiver sessões

    def adicionar_musculacao(self, ficha, nome, grupo, series, repeticoes, carga):
        # COMPOSIÇÃO: quem cria o exercício é a própria ficha.
        exercicio = ficha.adicionar_musculacao(nome, grupo, series, repeticoes, carga)
        self.repo.salvar_exercicio(ficha, exercicio)
        return exercicio

    def adicionar_cardio(self, ficha, nome, duracao, distancia):
        distancia = distancia if str(distancia).strip() else 0   # vazio = 0 km
        exercicio = ficha.adicionar_cardio(nome, duracao, distancia)
        self.repo.salvar_exercicio(ficha, exercicio)
        return exercicio

    def adicionar_isometrico(self, ficha, nome, grupo, series, tempo):
        exercicio = ficha.adicionar_isometrico(nome, grupo, series, tempo)
        self.repo.salvar_exercicio(ficha, exercicio)
        return exercicio

    def remover_exercicio(self, ficha, exercicio):
        self.repo.remover_exercicio(ficha, exercicio)

    # =====================================================================
    # Sessões
    # =====================================================================
    @staticmethod
    def campos_registro(exercicio):
        """Campos que a tela de sessão mostra para cada tipo de exercício.

        Devolve uma lista de (chave, rótulo, valor planejado na ficha).
        As chaves são as do RegistroExercicio: series, repeticoes e carga.
        """
        if isinstance(exercicio, ExercicioMusculacao):
            return [("series", "Séries", exercicio.series),
                    ("repeticoes", "Reps", exercicio.repeticoes),
                    ("carga", "Carga (kg)", f"{exercicio.carga_kg:g}")]
        if isinstance(exercicio, ExercicioCardio):
            # No cardio, o registro guarda os minutos feitos em "repeticoes".
            return [("repeticoes", "Minutos", max(1, round(exercicio.duracao_min)))]
        # Isométrico: guarda os segundos de cada série em "repeticoes".
        return [("series", "Séries", exercicio.series),
                ("repeticoes", "Segundos", max(1, round(exercicio.tempo_s)))]

    def registrar_sessao(self, aluno, ficha, data, duracao, observacao, feitos):
        """feitos: lista de (exercicio, {chave: texto digitado}) só dos marcados."""
        if aluno is None or ficha is None:
            raise ValueError("Escolha o aluno e a ficha.")
        if not str(data).strip():
            data = date.today()
        sessao = SessaoTreino(data, ficha, duracao, observacao)
        for exercicio, valores in feitos:
            try:
                # COMPOSIÇÃO: o registro é criado pela própria sessão.
                sessao.registrar_exercicio(exercicio.nome,
                                           valores.get("series", 1),
                                           valores.get("repeticoes", 1),
                                           valores.get("carga", 0))
            except ValueError as erro:
                raise ValueError(f"{exercicio.nome}: {erro}") from erro
        if not sessao.registros:
            raise ValueError("Marque pelo menos um exercício que foi feito.")
        self.repo.registrar_sessao(aluno, sessao)
        return sessao

    @staticmethod
    def historico(aluno):
        return sorted(aluno.sessoes, key=lambda sessao: sessao.data)

    # =====================================================================
    # Relatórios (DEPENDÊNCIA: o RelatorioEvolucao recebe as sessões por parâmetro)
    # =====================================================================
    @staticmethod
    def exercicios_com_carga(aluno):
        nomes = []
        for sessao in aluno.sessoes:
            for registro in sessao.registros:
                if registro.carga_kg > 0 and registro.exercicio.nome not in nomes:
                    nomes.append(registro.exercicio.nome)
        return nomes

    def evolucao_carga(self, aluno, nome_exercicio):
        evolucao = self.relatorio.evolucao_carga(aluno.sessoes, nome_exercicio)
        variacao = self.relatorio.variacao_carga(aluno.sessoes, nome_exercicio)
        return evolucao, variacao

    def volume_por_semana(self, aluno):
        return self.relatorio.volume_por_semana(aluno.sessoes)

    def imc(self, aluno):
        return self.relatorio.classificar_imc(aluno)
