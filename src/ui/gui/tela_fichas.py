"""Tela de fichas e exercícios: criar/excluir fichas e montar os exercícios."""

from tkinter import ttk

from models.exercicio import ExercicioCardio, ExercicioIsometrico, ExercicioMusculacao
from ui.gui.componentes import (JanelaFormulario, Seletor, Tabela, confirmar, criar_cartao,
                                erro)
from ui.gui.controlador import formatar_cpf, nome_do_tipo
from ui.gui.tela_base import TelaBase

# tag usada para colorir a linha de cada tipo de exercício na tabela
TAGS = {ExercicioMusculacao: "musculacao", ExercicioCardio: "cardio",
        ExercicioIsometrico: "isometrico"}


class TelaFichas(TelaBase):
    titulo = "Fichas e exercícios"
    subtitulo = "Monte os treinos (A, B, C...) com exercícios de musculação, cardio e isométricos"

    def montar(self):
        self.seletor = Seletor(self, "Aluno:", lambda a: f"{a.nome} ({formatar_cpf(a.cpf)})",
                               ao_mudar=self.atualizar_fichas)
        self.seletor.pack(anchor="w", pady=(0, 14))

        corpo = ttk.Frame(self)
        corpo.pack(fill="both", expand=True)
        corpo.columnconfigure(0, weight=2)
        corpo.columnconfigure(1, weight=5)
        corpo.rowconfigure(0, weight=1)

        # ---------- esquerda: fichas do aluno ----------
        esquerda = criar_cartao(corpo, "Fichas")
        esquerda.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        botoes = ttk.Frame(esquerda, style="Cartao.TFrame")
        botoes.pack(fill="x", pady=(0, 10))
        ttk.Button(botoes, text="+ Nova ficha", style="Primario.TButton",
                   command=self.nova_ficha).pack(side="left")
        ttk.Button(botoes, text="Excluir", style="Perigo.TButton",
                   command=self.excluir_ficha).pack(side="left", padx=8)
        self.tabela_fichas = Tabela(esquerda, [("nome", "Ficha", 110, "w"),
                                               ("qtd", "Exerc.", 60, "center"),
                                               ("volume", "Volume", 80, "center")], altura=12)
        self.tabela_fichas.pack(fill="both", expand=True)
        self.tabela_fichas.ao_selecionar(self.atualizar_exercicios)

        # ---------- direita: exercícios da ficha ----------
        direita = criar_cartao(corpo)
        direita.grid(row=0, column=1, sticky="nsew")
        self.titulo_ficha = ttk.Label(direita, text="Exercícios", style="CartaoTitulo.TLabel")
        self.titulo_ficha.pack(anchor="w", pady=(0, 10))
        botoes2 = ttk.Frame(direita, style="Cartao.TFrame")
        botoes2.pack(fill="x", pady=(0, 10))
        for texto, funcao in [("+ Musculação", self.add_musculacao),
                              ("+ Cardio", self.add_cardio),
                              ("+ Isométrico", self.add_isometrico)]:
            ttk.Button(botoes2, text=texto, style="Primario.TButton",
                       command=funcao).pack(side="left", padx=(0, 8))
        ttk.Button(botoes2, text="Remover exercício", style="Perigo.TButton",
                   command=self.remover_exercicio).pack(side="right")

        self.tabela_exercicios = Tabela(direita, [
            ("tipo", "Tipo", 100, "w"), ("descricao", "Descrição", 330, "w"),
            ("volume", "Volume", 90, "center"),
        ], altura=12)
        self.tabela_exercicios.pack(fill="both", expand=True)

        rodape = ttk.Frame(direita, style="Cartao.TFrame")
        rodape.pack(fill="x", pady=(12, 0))
        ttk.Label(rodape, style="CartaoSuave.TLabel",
                  text="Volume: musculação = séries × reps × carga · cardio = minutos · "
                       "isométrico = séries × segundos").pack(side="left")
        self.total = ttk.Label(rodape, text="", style="CartaoTitulo.TLabel")
        self.total.pack(side="right")

    # ---------- atualizar ----------
    def atualizar(self):
        self.seletor.definir_itens(self.ctrl.repo.alunos)
        self.atualizar_fichas()

    def atualizar_fichas(self):
        aluno = self.seletor.selecionado
        anterior = self.tabela_fichas.selecionado
        self.tabela_fichas.limpar()
        if aluno is not None:
            for ficha in aluno.fichas:
                self.tabela_fichas.adicionar(
                    (ficha.nome, len(ficha.exercicios), f"{ficha.calcular_volume_total():g}"),
                    ficha)
            if anterior in aluno.fichas:
                self.tabela_fichas.selecionar(anterior)
            elif aluno.fichas:
                self.tabela_fichas.selecionar(aluno.fichas[0])
        self.atualizar_exercicios()

    def atualizar_exercicios(self):
        ficha = self.tabela_fichas.selecionado
        self.tabela_exercicios.limpar()
        if ficha is None:
            self.titulo_ficha.configure(text="Exercícios (crie ou selecione uma ficha)")
            self.total.configure(text="")
            return
        self.titulo_ficha.configure(text=f"Exercícios do {ficha.nome}")
        for exercicio in ficha.exercicios:
            # POLIMORFISMO: descricao() e calcular_volume() de cada tipo de exercício
            self.tabela_exercicios.adicionar(
                (nome_do_tipo(exercicio), exercicio.descricao(),
                 f"{exercicio.calcular_volume():g}"),
                exercicio, tag=TAGS.get(type(exercicio)))
        self.total.configure(text=f"Volume total: {ficha.calcular_volume_total():g}")

    def _atualizar_tudo(self):
        """Depois de mudar exercícios: o volume na tabela de fichas também muda."""
        self.atualizar_fichas()

    # ---------- fichas ----------
    def nova_ficha(self):
        aluno = self.seletor.selecionado
        if aluno is None:
            erro(self, "Cadastre um aluno primeiro (tela Alunos).")
            return
        sugestao = f"Treino {chr(ord('A') + len(aluno.fichas))}" if len(aluno.fichas) < 26 else ""

        def salvar(v):
            ficha = self.ctrl.criar_ficha(aluno, v["nome"])
            self.atualizar_fichas()
            self.tabela_fichas.selecionar(ficha)
            self.avisar(f"{ficha.nome} criada para {aluno.nome}")

        JanelaFormulario(self, "Nova ficha", [("nome", "Nome da ficha", sugestao)], salvar,
                         subtitulo=f"Aluno: {aluno.nome}", texto_botao="Criar")

    def excluir_ficha(self):
        aluno, ficha = self.seletor.selecionado, self.tabela_fichas.selecionado
        if ficha is None:
            erro(self, "Selecione uma ficha primeiro.")
            return
        if not confirmar(self, f"Excluir {ficha.nome} de {aluno.nome}?"):
            return
        try:
            self.ctrl.excluir_ficha(aluno, ficha)
        except ValueError as problema:
            erro(self, problema)
            return
        self.atualizar_fichas()
        self.avisar(f"{ficha.nome} foi excluída")

    # ---------- exercícios ----------
    def _ficha_selecionada(self):
        ficha = self.tabela_fichas.selecionado
        if ficha is None:
            erro(self, "Crie ou selecione uma ficha primeiro.")
        return ficha

    def _abrir_formulario(self, titulo, campos, criar):
        ficha = self._ficha_selecionada()
        if ficha is None:
            return

        def salvar(v):
            exercicio = criar(ficha, v)
            self._atualizar_tudo()
            self.avisar(f"Adicionado: {exercicio.descricao()}")

        JanelaFormulario(self, titulo, campos, salvar, subtitulo=f"Ficha: {ficha.nome}",
                         texto_botao="Adicionar")

    def add_musculacao(self):
        self._abrir_formulario("Exercício de musculação", [
            ("nome", "Nome", ""), ("grupo", "Grupo muscular", ""),
            ("series", "Séries", ""), ("repeticoes", "Repetições", ""),
            ("carga", "Carga (kg)", ""),
        ], lambda ficha, v: self.ctrl.adicionar_musculacao(
            ficha, v["nome"], v["grupo"], v["series"], v["repeticoes"], v["carga"]))

    def add_cardio(self):
        self._abrir_formulario("Exercício de cardio", [
            ("nome", "Nome", ""), ("duracao", "Duração (min)", ""),
            ("distancia", "Distância (km)", "0"),
        ], lambda ficha, v: self.ctrl.adicionar_cardio(
            ficha, v["nome"], v["duracao"], v["distancia"]))

    def add_isometrico(self):
        self._abrir_formulario("Exercício isométrico", [
            ("nome", "Nome", ""), ("grupo", "Grupo muscular", ""),
            ("series", "Séries", ""), ("tempo", "Tempo por série (s)", ""),
        ], lambda ficha, v: self.ctrl.adicionar_isometrico(
            ficha, v["nome"], v["grupo"], v["series"], v["tempo"]))

    def remover_exercicio(self):
        ficha = self._ficha_selecionada()
        if ficha is None:
            return
        exercicio = self.tabela_exercicios.selecionado
        if exercicio is None:
            erro(self, "Selecione um exercício na tabela.")
            return
        if confirmar(self, f"Remover {exercicio.nome} do {ficha.nome}?"):
            self.ctrl.remover_exercicio(ficha, exercicio)
            self._atualizar_tudo()
            self.avisar(f"{exercicio.nome} foi removido")
