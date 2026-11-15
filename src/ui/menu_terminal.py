"""Menu do terminal (nível 2): acessa todos os modelos e funcionalidades.

Os dados ficam no RepositorioMemoria e somem ao fechar o programa
(o banco de dados entra no nível 3).
"""

from datetime import date

from models.exercicio import ExercicioCardio, ExercicioMusculacao
from models.ficha_treino import FichaTreino
from models.pessoa import Aluno, Instrutor
from models.sessao_treino import SessaoTreino
from models.validacao import inteiro_positivo, numero_positivo, texto_obrigatorio
from services.relatorio import RelatorioEvolucao
from ui.dados_exemplo import carregar_dados_exemplo


def formatar_cpf(cpf):
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def barra(valor, maximo, largura=25):
    """Barrinha de texto para os relatórios, ex.: ██████████"""
    if maximo <= 0:
        return ""
    return "█" * max(1, round(valor / maximo * largura))


class MenuTerminal:

    def __init__(self, repositorio, pausar=True):
        self.repo = repositorio            # onde os alunos e instrutores ficam guardados
        self.relatorio = RelatorioEvolucao()
        self.pausar = pausar               # nos testes, desligamos a pausa

    # =====================================================================
    # Funções de entrada: repetem a pergunta até o valor ser válido,
    # em vez de deixar o programa quebrar.
    # =====================================================================
    def ler_valor(self, mensagem, validar, padrao=None):
        """Pede um valor e valida. Se o usuário der Enter e houver padrão, usa o padrão."""
        while True:
            texto = input(mensagem).strip()
            if texto == "" and padrao is not None:
                return padrao
            try:
                return validar(texto)
            except ValueError as erro:
                print(f"  ✗ Erro: {erro}")

    def ler_texto(self, mensagem, campo):
        return self.ler_valor(mensagem, lambda t: texto_obrigatorio(t, campo))

    def ler_inteiro(self, mensagem, campo, padrao=None):
        return self.ler_valor(mensagem, lambda t: inteiro_positivo(t, campo), padrao)

    def ler_numero(self, mensagem, campo, padrao=None, permitir_zero=False):
        return self.ler_valor(
            mensagem, lambda t: numero_positivo(t, campo, permitir_zero), padrao)

    def ler_opcao(self, maximo):
        def validar(texto):
            if not texto.isdigit() or int(texto) > maximo:
                raise ValueError(f"opção inválida, digite um número de 0 a {maximo}.")
            return int(texto)
        return self.ler_valor("Opção: ", validar)

    def confirmar(self, mensagem):
        def validar(texto):
            if texto.lower() not in ("s", "n"):
                raise ValueError("responda com s ou n.")
            return texto.lower() == "s"
        return self.ler_valor(f"{mensagem} (s/n): ", validar)

    def ler_cpf_novo(self):
        def validar(texto):
            digitos = "".join(c for c in texto if c.isdigit())
            if len(digitos) != 11:
                raise ValueError("O CPF precisa ter 11 dígitos.")
            if self.repo.cpf_em_uso(digitos):
                raise ValueError("Já existe uma pessoa cadastrada com esse CPF.")
            return digitos
        return self.ler_valor("CPF: ", validar)

    def ler_data(self):
        def validar(texto):
            return SessaoTreino._converter_data(texto)
        hoje = date.today()
        return self.ler_valor(f"Data (DD/MM/AAAA) [Enter = hoje, {hoje:%d/%m/%Y}]: ",
                              validar, padrao=hoje)

    def editar_campo(self, objeto, atributo, rotulo):
        """Mostra o valor atual; Enter mantém, senão o setter da classe valida."""
        atual = getattr(objeto, atributo)
        while True:
            texto = input(f"{rotulo} [{atual:g}]: " if isinstance(atual, float)
                          else f"{rotulo} [{atual}]: ").strip()
            if texto == "":
                return
            try:
                setattr(objeto, atributo, texto)
                return
            except ValueError as erro:
                print(f"  ✗ Erro: {erro}")

    def escolher(self, itens, texto_item, vazio):
        """Lista os itens numerados e devolve o escolhido (ou None se cancelar)."""
        if not itens:
            print(f"  {vazio}")
            return None
        for numero, item in enumerate(itens, start=1):
            print(f"  {numero} - {texto_item(item)}")
        print("  0 - Cancelar")
        opcao = self.ler_opcao(len(itens))
        return None if opcao == 0 else itens[opcao - 1]

    def escolher_aluno(self):
        print("\nEscolha o aluno:")
        return self.escolher(self.repo.alunos, lambda a: f"{a.nome} ({formatar_cpf(a.cpf)})",
                             "Nenhum aluno cadastrado. Cadastre um na opção 1.")

    def escolher_instrutor(self):
        print("\nEscolha o instrutor:")
        return self.escolher(self.repo.instrutores,
                             lambda i: f"{i.nome} (CREF {i.cref})",
                             "Nenhum instrutor cadastrado. Cadastre um na opção 2.")

    def escolher_ficha(self, aluno):
        print(f"\nEscolha a ficha de {aluno.nome}:")
        return self.escolher(aluno.fichas,
                             lambda f: f"{f.nome} ({len(f.exercicios)} exercício(s))",
                             f"{aluno.nome} não tem fichas. Crie uma na opção 3.")

    # =====================================================================
    # Telas
    # =====================================================================
    @staticmethod
    def titulo(texto):
        print(f"\n{'=' * 50}\n  {texto}\n{'=' * 50}")

    def esperar_enter(self):
        if self.pausar:
            input("\nPressione Enter para continuar...")

    def submenu(self, titulo, opcoes):
        """Mostra um submenu até o usuário escolher 0 (Voltar).

        opcoes: lista de (texto, função que executa a opção).
        """
        while True:
            self.titulo(titulo)
            for numero, (texto, _) in enumerate(opcoes, start=1):
                print(f"  {numero} - {texto}")
            print("  0 - Voltar")
            opcao = self.ler_opcao(len(opcoes))
            if opcao == 0:
                return
            opcoes[opcao - 1][1]()
            self.esperar_enter()

    def executar(self):
        # (texto, função, pausar depois?) — os submenus já pausam sozinhos.
        opcoes = [
            ("Alunos", self.menu_alunos, False),
            ("Instrutores", self.menu_instrutores, False),
            ("Fichas de treino", self.menu_fichas, False),
            ("Exercícios de uma ficha", self.menu_exercicios, False),
            ("Ver ficha", self.ver_ficha, True),
            ("Registrar sessão de treino", self.registrar_sessao, True),
            ("Histórico de sessões", self.ver_historico, True),
            ("Relatórios", self.menu_relatorios, False),
            ("Carregar dados de exemplo", self.carregar_exemplo, True),
        ]
        while True:
            self.titulo("GERENCIADOR DE TREINOS")
            for numero, (texto, _, _) in enumerate(opcoes, start=1):
                print(f"  {numero} - {texto}")
            print("  0 - Sair")
            opcao = self.ler_opcao(len(opcoes))
            if opcao == 0:
                print("\nAté o próximo treino! "
                      "(Os dados não foram salvos: o banco de dados entra no nível 3.)")
                return
            _, funcao, pausar_depois = opcoes[opcao - 1]
            funcao()
            if pausar_depois:
                self.esperar_enter()

    # =====================================================================
    # 1 - Alunos
    # =====================================================================
    def menu_alunos(self):
        self.submenu("ALUNOS", [
            ("Cadastrar aluno", self.cadastrar_aluno),
            ("Listar alunos", self.listar_alunos),
            ("Editar aluno", self.editar_aluno),
            ("Excluir aluno", self.excluir_aluno),
        ])

    def cadastrar_aluno(self):
        print("\n--- Cadastrar aluno ---")
        nome = self.ler_texto("Nome: ", "nome")
        cpf = self.ler_cpf_novo()
        idade = self.ler_inteiro("Idade: ", "idade")
        peso = self.ler_numero("Peso (kg): ", "peso (kg)")
        altura = self.ler_numero("Altura (m, ex.: 1.75): ", "altura (m)")
        aluno = Aluno(nome, cpf, idade, peso, altura)
        self.repo.adicionar_aluno(aluno)
        print(f"\n✓ Aluno cadastrado: {aluno.apresentar()}")

    def listar_alunos(self):
        print("\n--- Alunos cadastrados ---")
        if not self.repo.alunos:
            print("  Nenhum aluno cadastrado.")
        for aluno in self.repo.alunos:
            instrutor = self.repo.instrutor_do_aluno(aluno)
            print(f"\n  {aluno.apresentar()}")   # polimorfismo: apresentar() do Aluno
            print(f"    CPF {formatar_cpf(aluno.cpf)} | altura {aluno.altura_m:g} m")
            print(f"    Instrutor: {instrutor.nome if instrutor else 'nenhum'}"
                  f" | {len(aluno.fichas)} ficha(s) | {len(aluno.sessoes)} sessão(ões)")

    def editar_aluno(self):
        aluno = self.escolher_aluno()
        if aluno is None:
            return
        print("\nDigite o novo valor ou Enter para manter. (O CPF não pode ser alterado.)")
        self.editar_campo(aluno, "nome", "Nome")
        self.editar_campo(aluno, "idade", "Idade")
        self.editar_campo(aluno, "peso_kg", "Peso (kg)")
        self.editar_campo(aluno, "altura_m", "Altura (m)")
        print(f"\n✓ Dados atualizados: {aluno.apresentar()}")

    def excluir_aluno(self):
        aluno = self.escolher_aluno()
        if aluno is None:
            return
        if self.confirmar(f"Excluir {aluno.nome} com todas as fichas e sessões?"):
            self.repo.remover_aluno(aluno.cpf)
            print(f"✓ {aluno.nome} foi excluído.")
        else:
            print("Exclusão cancelada.")

    # =====================================================================
    # 2 - Instrutores
    # =====================================================================
    def menu_instrutores(self):
        self.submenu("INSTRUTORES", [
            ("Cadastrar instrutor", self.cadastrar_instrutor),
            ("Listar instrutores e seus alunos", self.listar_instrutores),
            ("Vincular aluno a um instrutor", self.vincular_aluno),
            ("Desvincular aluno", self.desvincular_aluno),
            ("Excluir instrutor", self.excluir_instrutor),
        ])

    def cadastrar_instrutor(self):
        print("\n--- Cadastrar instrutor ---")
        nome = self.ler_texto("Nome: ", "nome")
        cpf = self.ler_cpf_novo()
        idade = self.ler_inteiro("Idade: ", "idade")
        cref = self.ler_texto("CREF (ex.: 012345-G/DF): ", "CREF")
        instrutor = Instrutor(nome, cpf, idade, cref)
        self.repo.adicionar_instrutor(instrutor)
        print(f"\n✓ Instrutor cadastrado: {instrutor.apresentar()}")

    def listar_instrutores(self):
        print("\n--- Instrutores ---")
        if not self.repo.instrutores:
            print("  Nenhum instrutor cadastrado.")
        for instrutor in self.repo.instrutores:
            print(f"\n  {instrutor.apresentar()}")  # polimorfismo: apresentar() do Instrutor
            for aluno in instrutor.alunos:
                print(f"    - {aluno.nome}")

    def vincular_aluno(self):
        instrutor = self.escolher_instrutor()
        if instrutor is None:
            return
        aluno = self.escolher_aluno()
        if aluno is None:
            return
        try:
            self.repo.vincular(instrutor, aluno)
            print(f"✓ {aluno.nome} agora é acompanhado por {instrutor.nome}.")
        except ValueError as erro:
            print(f"  ✗ Erro: {erro}")

    def desvincular_aluno(self):
        instrutor = self.escolher_instrutor()
        if instrutor is None:
            return
        print(f"\nAlunos de {instrutor.nome}:")
        aluno = self.escolher(instrutor.alunos, lambda a: a.nome,
                              f"{instrutor.nome} não acompanha nenhum aluno.")
        if aluno is None:
            return
        instrutor.desvincular_aluno(aluno.cpf)
        print(f"✓ {aluno.nome} foi desvinculado de {instrutor.nome}.")

    def excluir_instrutor(self):
        instrutor = self.escolher_instrutor()
        if instrutor is None:
            return
        if self.confirmar(f"Excluir {instrutor.nome}? (os alunos continuam cadastrados)"):
            self.repo.remover_instrutor(instrutor.cpf)
            print(f"✓ {instrutor.nome} foi excluído.")
        else:
            print("Exclusão cancelada.")

    # =====================================================================
    # 3 - Fichas
    # =====================================================================
    def menu_fichas(self):
        self.submenu("FICHAS DE TREINO", [
            ("Criar ficha para um aluno", self.criar_ficha),
            ("Listar fichas de um aluno", self.listar_fichas),
            ("Excluir ficha", self.excluir_ficha),
        ])

    def criar_ficha(self):
        aluno = self.escolher_aluno()
        if aluno is None:
            return

        def validar(texto):
            ficha = FichaTreino(texto)
            aluno.adicionar_ficha(ficha)   # lança erro se o nome já existir
            return ficha

        ficha = self.ler_valor("Nome da ficha (ex.: Treino A): ", validar)
        print(f"✓ {ficha.nome} criada para {aluno.nome}. "
              "Adicione exercícios na opção 4 do menu principal.")

    def listar_fichas(self):
        aluno = self.escolher_aluno()
        if aluno is None:
            return
        print(f"\n--- Fichas de {aluno.nome} ---")
        if not aluno.fichas:
            print("  Nenhuma ficha.")
        for ficha in aluno.fichas:
            print(f"  - {ficha.nome}: {len(ficha.exercicios)} exercício(s), "
                  f"volume total {ficha.calcular_volume_total():g}")

    def excluir_ficha(self):
        aluno = self.escolher_aluno()
        if aluno is None:
            return
        ficha = self.escolher_ficha(aluno)
        if ficha is None:
            return
        if any(sessao.ficha is ficha for sessao in aluno.sessoes):
            print("  ✗ Erro: essa ficha já tem sessões registradas e não pode ser excluída.")
            return
        if self.confirmar(f"Excluir {ficha.nome}?"):
            aluno.remover_ficha(ficha.nome)
            print(f"✓ {ficha.nome} foi excluída.")

    # =====================================================================
    # 4 - Exercícios de uma ficha
    # =====================================================================
    def menu_exercicios(self):
        aluno = self.escolher_aluno()
        if aluno is None:
            self.esperar_enter()
            return
        ficha = self.escolher_ficha(aluno)
        if ficha is None:
            self.esperar_enter()
            return
        self.submenu(f"EXERCÍCIOS — {ficha.nome} de {aluno.nome}", [
            ("Adicionar exercício", lambda: self.adicionar_exercicio(ficha)),
            ("Remover exercício", lambda: self.remover_exercicio(ficha)),
            ("Ver exercícios da ficha", lambda: print("\n" + ficha.descricao())),
        ])

    def adicionar_exercicio(self, ficha):
        print("\nTipo de exercício:")
        print("  1 - Musculação (séries, repetições e carga)")
        print("  2 - Cardio (duração e distância)")
        print("  3 - Isométrico (séries e tempo, ex.: prancha)")
        print("  0 - Cancelar")
        tipo = self.ler_opcao(3)
        if tipo == 0:
            return

        def nome_livre(texto):
            nome = texto_obrigatorio(texto, "nome do exercício")
            if ficha.buscar_exercicio(nome) is not None:
                raise ValueError(f"a ficha já tem um exercício chamado '{nome}'.")
            return nome

        nome = self.ler_valor("Nome do exercício: ", nome_livre)
        # COMPOSIÇÃO: quem cria o exercício é a própria ficha.
        if tipo == 1:
            grupo = self.ler_texto("Grupo muscular: ", "grupo muscular")
            series = self.ler_inteiro("Séries: ", "séries")
            repeticoes = self.ler_inteiro("Repetições: ", "repetições")
            carga = self.ler_numero("Carga (kg): ", "carga (kg)", permitir_zero=True)
            exercicio = ficha.adicionar_musculacao(nome, grupo, series, repeticoes, carga)
        elif tipo == 2:
            duracao = self.ler_numero("Duração (min): ", "duração (min)")
            distancia = self.ler_numero("Distância (km) [Enter = 0]: ", "distância (km)",
                                        padrao=0, permitir_zero=True)
            exercicio = ficha.adicionar_cardio(nome, duracao, distancia)
        else:
            grupo = self.ler_texto("Grupo muscular: ", "grupo muscular")
            series = self.ler_inteiro("Séries: ", "séries")
            tempo = self.ler_numero("Tempo de cada série (s): ", "tempo (s)")
            exercicio = ficha.adicionar_isometrico(nome, grupo, series, tempo)
        print(f"✓ Adicionado: {exercicio.descricao()} | volume {exercicio.calcular_volume():g}")

    def remover_exercicio(self, ficha):
        print(f"\nExercícios de {ficha.nome}:")
        exercicio = self.escolher(ficha.exercicios, lambda e: e.descricao(),
                                  "A ficha não tem exercícios.")
        if exercicio is None:
            return
        ficha.remover_exercicio(exercicio.nome)
        print(f"✓ {exercicio.nome} foi removido de {ficha.nome}.")

    # =====================================================================
    # 5 - Ver ficha
    # =====================================================================
    def ver_ficha(self):
        aluno = self.escolher_aluno()
        if aluno is None:
            return
        ficha = self.escolher_ficha(aluno)
        if ficha is None:
            return
        print(f"\n--- Ficha de {aluno.nome} ---")
        # POLIMORFISMO: cada exercício mostra a própria descrição e o próprio volume.
        print(ficha.descricao())

    # =====================================================================
    # 6 - Registrar sessão
    # =====================================================================
    def registrar_sessao(self):
        aluno = self.escolher_aluno()
        if aluno is None:
            return
        ficha = self.escolher_ficha(aluno)
        if ficha is None:
            return
        if not ficha.exercicios:
            print(f"  ✗ Erro: {ficha.nome} não tem exercícios. Adicione na opção 4.")
            return

        print(f"\n--- Registrar sessão: {ficha.nome} ---")
        data = self.ler_data()
        duracao = self.ler_numero("Duração do treino (min): ", "duração (min)")
        observacao = input("Observação (opcional): ").strip()
        sessao = SessaoTreino(data, ficha, duracao, observacao)

        print("\nPara cada exercício, Enter usa o valor planejado na ficha.")
        for exercicio in ficha.exercicios:
            print(f"\n> {exercicio.descricao()}")
            if not self.confirmar("  Fez esse exercício?"):
                continue
            if isinstance(exercicio, ExercicioMusculacao):
                series = self.ler_inteiro(f"  Séries [{exercicio.series}]: ", "séries",
                                          exercicio.series)
                repeticoes = self.ler_inteiro(f"  Repetições [{exercicio.repeticoes}]: ",
                                              "repetições", exercicio.repeticoes)
                carga = self.ler_numero(f"  Carga (kg) [{exercicio.carga_kg:g}]: ",
                                        "carga (kg)", exercicio.carga_kg, permitir_zero=True)
            elif isinstance(exercicio, ExercicioCardio):
                series = 1
                repeticoes = self.ler_inteiro(
                    f"  Minutos feitos [{exercicio.duracao_min:g}]: ", "minutos",
                    int(exercicio.duracao_min))
                carga = 0
            else:                                      # isométrico
                series = self.ler_inteiro(f"  Séries [{exercicio.series}]: ", "séries",
                                          exercicio.series)
                repeticoes = self.ler_inteiro(
                    f"  Segundos por série [{exercicio.tempo_s:g}]: ", "segundos",
                    int(exercicio.tempo_s))
                carga = 0
            # COMPOSIÇÃO: o registro é criado pela própria sessão.
            sessao.registrar_exercicio(exercicio.nome, series, repeticoes, carga)

        if not sessao.registros:
            print("\nNenhum exercício feito: a sessão não foi registrada.")
            return
        aluno.registrar_sessao(sessao)
        print("\n✓ Sessão registrada:")
        print(sessao.resumo())

    # =====================================================================
    # 7 - Histórico
    # =====================================================================
    def ver_historico(self):
        aluno = self.escolher_aluno()
        if aluno is None:
            return
        print(f"\n--- Histórico de {aluno.nome} ---")
        if not aluno.sessoes:
            print("  Nenhuma sessão registrada. Registre uma na opção 6.")
            return
        for sessao in sorted(aluno.sessoes, key=lambda s: s.data):
            print()
            print(sessao.resumo())
        print(f"\nTotal: {len(aluno.sessoes)} sessão(ões)")

    # =====================================================================
    # 8 - Relatórios
    # =====================================================================
    def menu_relatorios(self):
        aluno = self.escolher_aluno()
        if aluno is None:
            self.esperar_enter()
            return
        self.submenu(f"RELATÓRIOS — {aluno.nome}", [
            ("Evolução de carga de um exercício", lambda: self.relatorio_carga(aluno)),
            ("Volume por semana", lambda: self.relatorio_volume(aluno)),
            ("IMC do aluno", lambda: self.relatorio_imc(aluno)),
        ])

    def relatorio_carga(self, aluno):
        # Só exercícios que já foram feitos com carga aparecem na lista.
        nomes = []
        for sessao in aluno.sessoes:
            for registro in sessao.registros:
                if registro.carga_kg > 0 and registro.exercicio.nome not in nomes:
                    nomes.append(registro.exercicio.nome)
        print("\nEscolha o exercício:")
        nome = self.escolher(nomes, lambda n: n,
                             "Ainda não há exercícios com carga registrados em sessões.")
        if nome is None:
            return
        # DEPENDÊNCIA: o relatório recebe as sessões por parâmetro e não as guarda.
        evolucao = self.relatorio.evolucao_carga(aluno.sessoes, nome)
        maior = max(carga for _, carga in evolucao)
        print(f"\n--- Evolução de carga: {nome} ---")
        for data, carga in evolucao:
            print(f"  {data:%d/%m/%Y}  {carga:>6g} kg  {barra(carga, maior)}")
        variacao = self.relatorio.variacao_carga(aluno.sessoes, nome)
        print(f"\n  Variação desde o primeiro treino: {variacao:+g} kg")

    def relatorio_volume(self, aluno):
        volumes = self.relatorio.volume_por_semana(aluno.sessoes)
        print("\n--- Volume por semana (séries × repetições × carga) ---")
        if not volumes:
            print("  Nenhuma sessão registrada.")
            return
        maior = max(volumes.values())
        for semana, volume in volumes.items():
            print(f"  {semana}  {volume:>8g} kg  {barra(volume, maior)}")

    def relatorio_imc(self, aluno):
        imc, faixa = self.relatorio.classificar_imc(aluno)
        print(f"\n--- IMC de {aluno.nome} ---")
        print(f"  Peso {aluno.peso_kg:g} kg | altura {aluno.altura_m:g} m")
        print(f"  IMC: {imc:.2f} — {faixa}")

    # =====================================================================
    # 9 - Dados de exemplo
    # =====================================================================
    def carregar_exemplo(self):
        if carregar_dados_exemplo(self.repo):
            print("\n✓ Dados de exemplo carregados: 1 instrutor, 2 alunos, "
                  "fichas e sessões de treino.")
        else:
            print("\nOs dados de exemplo já foram carregados.")
