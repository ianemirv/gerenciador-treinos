"""Tela de histórico: todas as sessões de um aluno, em ordem de data."""

import tkinter as tk
from tkinter import ttk

from ui.gui.componentes import Seletor, Tabela, criar_cartao
from ui.gui.controlador import formatar_cpf
from ui.gui.estilos import CORES, FONTES
from ui.gui.tela_base import TelaBase


class TelaHistorico(TelaBase):
    titulo = "Histórico de sessões"
    subtitulo = "Clique numa sessão para ver o que foi feito em cada exercício"

    def montar(self):
        self.seletor = Seletor(self, "Aluno:", lambda a: f"{a.nome} ({formatar_cpf(a.cpf)})",
                               ao_mudar=self.atualizar_sessoes)
        self.seletor.pack(anchor="w", pady=(0, 14))

        corpo = ttk.Frame(self)
        corpo.pack(fill="both", expand=True)
        corpo.columnconfigure(0, weight=3)
        corpo.columnconfigure(1, weight=2)
        corpo.rowconfigure(0, weight=1)

        esquerda = criar_cartao(corpo, padding=0)
        esquerda.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        self.tabela = Tabela(esquerda, [
            ("data", "Data", 100, "center"), ("ficha", "Ficha", 110, "w"),
            ("duracao", "Duração", 80, "center"), ("exercicios", "Exercícios", 90, "center"),
            ("volume", "Volume do dia", 110, "center"),
        ], altura=15)
        self.tabela.pack(fill="both", expand=True)
        self.tabela.ao_selecionar(self.mostrar_detalhe)

        direita = criar_cartao(corpo, "Detalhes da sessão")
        direita.grid(row=0, column=1, sticky="nsew")
        self.detalhe = tk.Text(direita, height=14, width=38, wrap="word", relief="flat",
                               background=CORES["fundo"], foreground=CORES["texto"],
                               font=FONTES["normal"], padx=12, pady=10, state="disabled")
        self.detalhe.pack(fill="both", expand=True)

        self.total = ttk.Label(self, style="Suave.TLabel")
        self.total.pack(anchor="w", pady=(10, 0))

    def atualizar(self):
        self.seletor.definir_itens(self.ctrl.repo.alunos)
        self.atualizar_sessoes()

    def atualizar_sessoes(self):
        aluno = self.seletor.selecionado
        self.tabela.limpar()
        sessoes = self.ctrl.historico(aluno) if aluno else []
        for sessao in sessoes:
            self.tabela.adicionar((f"{sessao.data:%d/%m/%Y}", sessao.ficha.nome,
                                   f"{sessao.duracao_min:g} min", len(sessao.registros),
                                   f"{sessao.calcular_volume_total():g} kg"), sessao)
        if sessoes:
            self.tabela.selecionar(sessoes[-1])   # mostra a mais recente
        self.total.configure(text=f"Total: {len(sessoes)} sessão(ões)" if aluno else
                             "Nenhum aluno cadastrado.")
        self.mostrar_detalhe()

    def mostrar_detalhe(self):
        sessao = self.tabela.selecionado
        texto = sessao.resumo() if sessao else "Nenhuma sessão registrada para este aluno."
        self.detalhe.configure(state="normal")
        self.detalhe.delete("1.0", "end")
        self.detalhe.insert("1.0", texto)
        self.detalhe.configure(state="disabled")
