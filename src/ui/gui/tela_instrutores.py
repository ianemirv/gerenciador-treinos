"""Tela de instrutores: cadastrar, excluir e vincular/desvincular alunos."""

from tkinter import ttk

from ui.gui.componentes import JanelaFormulario, Tabela, confirmar, criar_cartao, erro, info
from ui.gui.controlador import formatar_cpf
from ui.gui.tela_base import TelaBase


class TelaInstrutores(TelaBase):
    titulo = "Instrutores"
    subtitulo = "Cada instrutor acompanha seus alunos (associação)"

    def montar(self):
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(1, weight=1)

        # ---------- esquerda: instrutores ----------
        barra = ttk.Frame(self)
        barra.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        ttk.Button(barra, text="+ Cadastrar instrutor", style="Primario.TButton",
                   command=self.cadastrar).pack(side="left")
        ttk.Button(barra, text="Excluir", style="Perigo.TButton",
                   command=self.excluir).pack(side="left", padx=8)

        cartao = criar_cartao(self, padding=0)
        cartao.grid(row=1, column=0, sticky="nsew", padx=(0, 16))
        self.tabela = Tabela(cartao, [
            ("nome", "Nome", 170, "w"), ("cpf", "CPF", 120, "center"),
            ("idade", "Idade", 60, "center"), ("cref", "CREF", 110, "center"),
            ("alunos", "Alunos", 70, "center"),
        ], altura=14)
        self.tabela.pack(fill="both", expand=True)
        self.tabela.ao_selecionar(self.mostrar_alunos)

        # ---------- direita: alunos do instrutor selecionado ----------
        barra2 = ttk.Frame(self)
        barra2.grid(row=0, column=1, sticky="ew", pady=(0, 12))
        ttk.Button(barra2, text="Vincular aluno", style="Primario.TButton",
                   command=self.vincular).pack(side="left")
        ttk.Button(barra2, text="Desvincular", style="Secundario.TButton",
                   command=self.desvincular).pack(side="left", padx=8)

        lado = criar_cartao(self, padding=16)
        lado.grid(row=1, column=1, sticky="nsew")
        self.titulo_alunos = ttk.Label(lado, text="Alunos acompanhados",
                                       style="CartaoTitulo.TLabel")
        self.titulo_alunos.pack(anchor="w")
        self.apresentacao = ttk.Label(lado, style="CartaoSuave.TLabel", wraplength=320)
        self.apresentacao.pack(anchor="w", pady=(2, 10))
        self.tabela_alunos = Tabela(lado, [("nome", "Aluno", 160, "w"),
                                           ("imc", "IMC", 60, "center")], altura=10)
        self.tabela_alunos.pack(fill="both", expand=True)

    def atualizar(self):
        selecionado = self.tabela.selecionado
        self.tabela.limpar()
        for instrutor in self.ctrl.repo.instrutores:
            self.tabela.adicionar((instrutor.nome, formatar_cpf(instrutor.cpf), instrutor.idade,
                                   instrutor.cref, len(instrutor.alunos)), instrutor)
        if selecionado is not None:
            self.tabela.selecionar(selecionado)
        elif self.ctrl.repo.instrutores:
            self.tabela.selecionar(self.ctrl.repo.instrutores[0])
        self.mostrar_alunos()

    def mostrar_alunos(self):
        instrutor = self.tabela.selecionado
        self.tabela_alunos.limpar()
        if instrutor is None:
            self.titulo_alunos.configure(text="Alunos acompanhados")
            self.apresentacao.configure(text="Selecione um instrutor na tabela.")
            return
        self.titulo_alunos.configure(text=f"Alunos de {instrutor.nome}")
        self.apresentacao.configure(text=instrutor.apresentar())   # polimorfismo
        for aluno in instrutor.alunos:
            self.tabela_alunos.adicionar((aluno.nome, f"{aluno.calcular_imc():.2f}"), aluno)

    def _instrutor_selecionado(self):
        instrutor = self.tabela.selecionado
        if instrutor is None:
            erro(self, "Selecione um instrutor na tabela primeiro.")
        return instrutor

    # ---------- ações ----------
    def cadastrar(self):
        def salvar(v):
            instrutor = self.ctrl.cadastrar_instrutor(v["nome"], v["cpf"], v["idade"], v["cref"])
            self.atualizar()
            self.tabela.selecionar(instrutor)
            self.avisar(f"Instrutor cadastrado: {instrutor.nome}")

        JanelaFormulario(self, "Cadastrar instrutor", [
            ("nome", "Nome", ""), ("cpf", "CPF", ""), ("idade", "Idade", ""),
            ("cref", "CREF", ""),
        ], salvar, subtitulo="Ex. de CREF: 012345-G/DF")

    def excluir(self):
        instrutor = self._instrutor_selecionado()
        if instrutor is None:
            return
        if confirmar(self, f"Excluir {instrutor.nome}? Os alunos continuam cadastrados."):
            self.ctrl.excluir_instrutor(instrutor)
            self.atualizar()
            self.avisar(f"{instrutor.nome} foi excluído")

    def vincular(self):
        instrutor = self._instrutor_selecionado()
        if instrutor is None:
            return
        livres = self.ctrl.alunos_sem_instrutor()
        if not livres:
            info(self, "Todos os alunos já têm instrutor (ou não há alunos cadastrados).",
                 titulo="Aviso")
            return
        textos = [f"{aluno.nome} ({formatar_cpf(aluno.cpf)})" for aluno in livres]

        def salvar(v):
            if v["aluno"] not in textos:
                raise ValueError("Escolha um aluno da lista.")
            aluno = livres[textos.index(v["aluno"])]
            self.ctrl.vincular(instrutor, aluno)
            self.atualizar()
            self.avisar(f"{aluno.nome} agora é acompanhado por {instrutor.nome}")

        JanelaFormulario(self, "Vincular aluno", [("aluno", "Aluno", textos[0], textos)],
                         salvar, subtitulo=f"Instrutor: {instrutor.nome}. Só aparecem "
                                           "alunos que ainda não têm instrutor.",
                         texto_botao="Vincular")

    def desvincular(self):
        instrutor = self._instrutor_selecionado()
        if instrutor is None:
            return
        aluno = self.tabela_alunos.selecionado
        if aluno is None:
            erro(self, "Selecione um aluno na lista da direita.")
            return
        self.ctrl.desvincular(instrutor, aluno)
        self.atualizar()
        self.avisar(f"{aluno.nome} foi desvinculado de {instrutor.nome}")
