"""Tela de registrar sessão: o treino que o aluno fez num dia."""

import tkinter as tk
from datetime import date
from tkinter import ttk

from ui.gui.componentes import Seletor, criar_cartao, erro
from ui.gui.controlador import formatar_cpf, nome_do_tipo
from ui.gui.estilos import CORES, FONTES
from ui.gui.tela_base import TelaBase


class TelaSessao(TelaBase):
    titulo = "Registrar sessão de treino"
    subtitulo = "Marque os exercícios feitos. Os campos já vêm com o valor planejado na ficha."

    def montar(self):
        topo = ttk.Frame(self)
        topo.pack(fill="x", pady=(0, 14))
        self.seletor_aluno = Seletor(topo, "Aluno:", lambda a: f"{a.nome} ({formatar_cpf(a.cpf)})",
                                     ao_mudar=self.atualizar_fichas)
        self.seletor_aluno.pack(side="left")
        self.seletor_ficha = Seletor(topo, "Ficha:", lambda f: f.nome,
                                     ao_mudar=self.montar_exercicios, largura=16)
        self.seletor_ficha.pack(side="left", padx=(24, 0))

        corpo = ttk.Frame(self)
        corpo.pack(fill="both", expand=True)
        corpo.columnconfigure(0, weight=3)
        corpo.columnconfigure(1, weight=2)
        corpo.rowconfigure(1, weight=1)

        # ---------- dados do treino ----------
        dados = criar_cartao(corpo, "Dados do treino")
        dados.grid(row=0, column=0, sticky="nsew", padx=(0, 16), pady=(0, 16))
        campos = ttk.Frame(dados, style="Cartao.TFrame")
        campos.pack(fill="x")
        self.data = tk.StringVar(value=f"{date.today():%d/%m/%Y}")
        self.duracao = tk.StringVar()
        self.observacao = tk.StringVar()
        for coluna, (rotulo, variavel, largura) in enumerate([
                ("Data (DD/MM/AAAA)", self.data, 14), ("Duração (min)", self.duracao, 10),
                ("Observação (opcional)", self.observacao, 34)]):
            ttk.Label(campos, text=rotulo, style="CartaoSuave.TLabel").grid(
                row=0, column=coluna, sticky="w", padx=(0, 16))
            ttk.Entry(campos, textvariable=variavel, width=largura).grid(
                row=1, column=coluna, sticky="w", padx=(0, 16), pady=(2, 0))

        # ---------- exercícios da ficha ----------
        self.cartao_exercicios = criar_cartao(corpo, "Exercícios feitos")
        self.cartao_exercicios.grid(row=1, column=0, sticky="nsew", padx=(0, 16))
        self.lista = ttk.Frame(self.cartao_exercicios, style="Cartao.TFrame")
        self.lista.pack(fill="both", expand=True)
        ttk.Button(self.cartao_exercicios, text="Registrar sessão", style="Primario.TButton",
                   command=self.registrar).pack(anchor="e", pady=(12, 0))
        self.linhas = []   # (exercicio, variavel do "fez?", {chave: variavel})

        # ---------- resumo da última sessão ----------
        lado = criar_cartao(corpo, "Última sessão registrada")
        lado.grid(row=0, column=1, rowspan=2, sticky="nsew")
        self.resumo = tk.Text(lado, height=16, width=40, wrap="word", relief="flat",
                              background=CORES["fundo"], foreground=CORES["texto"],
                              font=FONTES["normal"], padx=12, pady=10, state="disabled")
        self.resumo.pack(fill="both", expand=True)

    # ---------- atualizar ----------
    def atualizar(self):
        self.seletor_aluno.definir_itens(self.ctrl.repo.alunos)
        self.atualizar_fichas()

    def atualizar_fichas(self):
        aluno = self.seletor_aluno.selecionado
        self.seletor_ficha.definir_itens(aluno.fichas if aluno else [])
        self.montar_exercicios()

    def montar_exercicios(self):
        """Cria uma linha por exercício da ficha, com os campos do tipo dele."""
        for widget in self.lista.winfo_children():
            widget.destroy()
        self.linhas = []
        ficha = self.seletor_ficha.selecionado
        if ficha is None or not ficha.exercicios:
            texto = ("Escolha um aluno que tenha fichas." if ficha is None else
                     f"{ficha.nome} não tem exercícios. Adicione na tela Fichas.")
            ttk.Label(self.lista, text=texto, style="CartaoSuave.TLabel").grid(row=0, column=0)
            return

        for linha, exercicio in enumerate(ficha.exercicios):
            fez = tk.BooleanVar(value=True)
            ttk.Checkbutton(self.lista, text=exercicio.nome, variable=fez,
                            style="Cartao.TCheckbutton").grid(
                row=linha, column=0, sticky="w", pady=5, padx=(0, 12))
            ttk.Label(self.lista, text=nome_do_tipo(exercicio), style="CartaoSuave.TLabel",
                      width=11).grid(row=linha, column=1, sticky="w")
            variaveis = {}
            # Cada tipo de exercício pede campos diferentes (ver campos_registro)
            for posicao, (chave, rotulo, valor) in enumerate(self.ctrl.campos_registro(exercicio)):
                coluna = 2 + posicao * 2
                ttk.Label(self.lista, text=rotulo, style="Cartao.TLabel").grid(
                    row=linha, column=coluna, sticky="e", padx=(8, 4))
                variavel = tk.StringVar(value=str(valor))
                ttk.Entry(self.lista, textvariable=variavel, width=7).grid(
                    row=linha, column=coluna + 1, sticky="w")
                variaveis[chave] = variavel
            self.linhas.append((exercicio, fez, variaveis))

    # ---------- registrar ----------
    def registrar(self):
        aluno, ficha = self.seletor_aluno.selecionado, self.seletor_ficha.selecionado
        feitos = [(exercicio, {chave: var.get() for chave, var in variaveis.items()})
                  for exercicio, fez, variaveis in self.linhas if fez.get()]
        try:
            sessao = self.ctrl.registrar_sessao(aluno, ficha, self.data.get(),
                                                self.duracao.get(), self.observacao.get(),
                                                feitos)
        except ValueError as problema:
            erro(self, problema)
            return
        self.mostrar_resumo(f"{aluno.nome}\n\n{sessao.resumo()}")
        self.duracao.set("")
        self.observacao.set("")
        self.montar_exercicios()   # volta os campos para os valores da ficha
        self.avisar(f"Sessão registrada para {aluno.nome}")

    def mostrar_resumo(self, texto):
        self.resumo.configure(state="normal")
        self.resumo.delete("1.0", "end")
        self.resumo.insert("1.0", texto)
        self.resumo.configure(state="disabled")
