"""Tela de alunos: listar, buscar, cadastrar, editar e excluir."""

import tkinter as tk
from tkinter import ttk

from ui.gui.componentes import JanelaFormulario, Tabela, confirmar, criar_cartao, erro
from ui.gui.controlador import formatar_cpf
from ui.gui.tela_base import TelaBase


class TelaAlunos(TelaBase):
    titulo = "Alunos"
    subtitulo = "Cadastre, edite e exclua alunos (dê dois cliques numa linha para editar)"

    def montar(self):
        barra = ttk.Frame(self)
        barra.pack(fill="x", pady=(0, 12))
        ttk.Button(barra, text="+ Cadastrar aluno", style="Primario.TButton",
                   command=self.cadastrar).pack(side="left")
        ttk.Button(barra, text="Editar", style="Secundario.TButton",
                   command=self.editar).pack(side="left", padx=8)
        ttk.Button(barra, text="Excluir", style="Perigo.TButton",
                   command=self.excluir).pack(side="left")

        # Busca por nome: filtra a tabela enquanto digita
        self.busca = tk.StringVar()
        self.busca.trace_add("write", lambda *_: self.atualizar())
        ttk.Entry(barra, textvariable=self.busca, width=28).pack(side="right")
        ttk.Label(barra, text="Buscar:").pack(side="right", padx=(0, 8))

        cartao = criar_cartao(self, padding=0)
        cartao.pack(fill="both", expand=True)
        self.tabela = Tabela(cartao, [
            ("nome", "Nome", 180, "w"), ("cpf", "CPF", 120, "center"),
            ("idade", "Idade", 60, "center"), ("peso", "Peso (kg)", 80, "center"),
            ("altura", "Altura (m)", 80, "center"), ("imc", "IMC", 70, "center"),
            ("instrutor", "Instrutor", 150, "w"), ("fichas", "Fichas", 60, "center"),
            ("sessoes", "Sessões", 70, "center"),
        ], altura=14)
        self.tabela.pack(fill="both", expand=True)
        self.tabela.ao_duplo_clique(self.editar)
        self.tabela.ao_selecionar(self.mostrar_detalhe)

        # Embaixo da tabela: o texto de apresentar() do aluno selecionado (polimorfismo)
        self.detalhe = ttk.Label(self, style="Suave.TLabel", text="")
        self.detalhe.pack(anchor="w", pady=(10, 0))

    def atualizar(self):
        selecionado = self.tabela.selecionado
        self.tabela.limpar()
        filtro = self.busca.get().strip().lower()
        for aluno in self.ctrl.repo.alunos:
            if filtro and filtro not in aluno.nome.lower():
                continue
            instrutor = self.ctrl.instrutor_do_aluno(aluno)
            self.tabela.adicionar((
                aluno.nome, formatar_cpf(aluno.cpf), aluno.idade, f"{aluno.peso_kg:g}",
                f"{aluno.altura_m:g}", f"{aluno.calcular_imc():.2f}",
                instrutor.nome if instrutor else "—", len(aluno.fichas), len(aluno.sessoes),
            ), aluno)
        if selecionado is not None:
            self.tabela.selecionar(selecionado)
        self.mostrar_detalhe()

    def mostrar_detalhe(self):
        aluno = self.tabela.selecionado
        self.detalhe.configure(text=aluno.apresentar() if aluno else
                               f"{len(self.ctrl.repo.alunos)} aluno(s) cadastrado(s).")

    def _aluno_selecionado(self):
        aluno = self.tabela.selecionado
        if aluno is None:
            erro(self, "Selecione um aluno na tabela primeiro.")
        return aluno

    # ---------- ações ----------
    def cadastrar(self):
        def salvar(v):
            aluno = self.ctrl.cadastrar_aluno(v["nome"], v["cpf"], v["idade"],
                                              v["peso"], v["altura"])
            self.atualizar()
            self.tabela.selecionar(aluno)
            self.avisar(f"Aluno cadastrado: {aluno.nome}")

        JanelaFormulario(self, "Cadastrar aluno", [
            ("nome", "Nome", ""), ("cpf", "CPF", ""), ("idade", "Idade", ""),
            ("peso", "Peso (kg)", ""), ("altura", "Altura (m)", ""),
        ], salvar, subtitulo="O CPF pode ser digitado com ou sem pontos. Ex.: altura 1.75")

    def editar(self):
        aluno = self._aluno_selecionado()
        if aluno is None:
            return

        def salvar(v):
            self.ctrl.editar_aluno(aluno, v["nome"], v["idade"], v["peso"], v["altura"])
            self.atualizar()
            self.avisar(f"Dados de {aluno.nome} atualizados")

        JanelaFormulario(self, "Editar aluno", [
            ("nome", "Nome", aluno.nome), ("idade", "Idade", aluno.idade),
            ("peso", "Peso (kg)", f"{aluno.peso_kg:g}"),
            ("altura", "Altura (m)", f"{aluno.altura_m:g}"),
        ], salvar, subtitulo=f"CPF {formatar_cpf(aluno.cpf)} (o CPF não pode ser alterado)")

    def excluir(self):
        aluno = self._aluno_selecionado()
        if aluno is None:
            return
        if confirmar(self, f"Excluir {aluno.nome} com todas as fichas e sessões?"):
            self.ctrl.excluir_aluno(aluno)
            self.atualizar()
            self.avisar(f"{aluno.nome} foi excluído")
