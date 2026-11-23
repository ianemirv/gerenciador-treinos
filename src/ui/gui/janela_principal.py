"""JanelaPrincipal: a janela do app, com o menu lateral e a área das telas.

Ela recebe o repositório (igual ao MenuTerminal), cria o ControladorGUI e
todas as telas. Clicar num item do menu lateral mostra a tela e chama
tela.atualizar() (POLIMORFISMO: cada tela se atualiza do seu jeito).
"""

import tkinter as tk
from pathlib import Path
from tkinter import ttk

from ui.gui.controlador import ControladorGUI
from ui.gui.estilos import CORES, FONTES, aplicar_estilos
from ui.gui.tela_alunos import TelaAlunos
from ui.gui.tela_fichas import TelaFichas
from ui.gui.tela_historico import TelaHistorico
from ui.gui.tela_inicio import TelaInicio
from ui.gui.tela_instrutores import TelaInstrutores
from ui.gui.tela_relatorios import TelaRelatorios
from ui.gui.tela_sessao import TelaSessao

# (chave, texto no menu lateral, classe da tela)
TELAS = [
    ("inicio", "Início", TelaInicio),
    ("alunos", "Alunos", TelaAlunos),
    ("instrutores", "Instrutores", TelaInstrutores),
    ("fichas", "Fichas e exercícios", TelaFichas),
    ("sessao", "Registrar sessão", TelaSessao),
    ("historico", "Histórico", TelaHistorico),
    ("relatorios", "Relatórios", TelaRelatorios),
]


class JanelaPrincipal(tk.Tk):

    def __init__(self, repositorio):
        super().__init__()
        self.repositorio = repositorio
        self.controlador = ControladorGUI(repositorio)
        self.title("Gerenciador de Treinos")
        self.geometry("1220x740")
        self.minsize(1040, 640)
        aplicar_estilos(self)
        self._aviso_agendado = None

        self._montar_menu_lateral()
        self._montar_area_principal()

        self.telas = {}
        for chave, _, classe in TELAS:
            tela = classe(self.area, self)
            tela.grid(row=0, column=0, sticky="nsew")   # todas no mesmo lugar, uma por cima da outra
            self.telas[chave] = tela
        self.mostrar("inicio")

        # Ao fechar no X: fecha o banco antes de sair
        self.protocol("WM_DELETE_WINDOW", self.sair)

    # ---------- montagem ----------
    def _montar_menu_lateral(self):
        lateral = ttk.Frame(self, style="Lateral.TFrame", width=230)
        lateral.pack(side="left", fill="y")
        lateral.pack_propagate(False)

        ttk.Label(lateral, text="Gerenciador\nde Treinos", style="Logo.TLabel",
                  justify="left").pack(anchor="w", padx=24, pady=(28, 4))
        ttk.Label(lateral, text="Orientação a Objetos · UnB",
                  style="LateralSuave.TLabel").pack(anchor="w", padx=24, pady=(0, 24))

        self.botoes_menu = {}
        for chave, texto, _ in TELAS:
            botao = ttk.Button(lateral, text=texto, style="Menu.TButton",
                               command=lambda c=chave: self.mostrar(c))
            botao.pack(fill="x")
            self.botoes_menu[chave] = botao

        ttk.Button(lateral, text="Sair", style="Menu.TButton",
                   command=self.sair).pack(side="bottom", fill="x", pady=(0, 16))
        nome_banco = Path(getattr(self.repositorio, "caminho", "memória")).name
        ttk.Label(lateral, text=f"Banco: {nome_banco}",
                  style="LateralSuave.TLabel").pack(side="bottom", anchor="w", padx=24, pady=8)

    def _montar_area_principal(self):
        direita = ttk.Frame(self)
        direita.pack(side="left", fill="both", expand=True)

        cabecalho = ttk.Frame(direita, padding=(28, 22, 28, 10))
        cabecalho.pack(fill="x")
        self.titulo = ttk.Label(cabecalho, style="Titulo.TLabel")
        self.titulo.pack(anchor="w")
        self.subtitulo = ttk.Label(cabecalho, style="Suave.TLabel")
        self.subtitulo.pack(anchor="w")

        # Barra de status embaixo: mostra a última ação feita
        self.status = tk.Label(direita, anchor="w", padx=28, pady=6, font=FONTES["normal"],
                               background=CORES["cartao"], foreground=CORES["texto_suave"])
        self.status.pack(side="bottom", fill="x")

        self.area = ttk.Frame(direita)
        self.area.pack(fill="both", expand=True)
        self.area.rowconfigure(0, weight=1)
        self.area.columnconfigure(0, weight=1)

    # ---------- navegação ----------
    def mostrar(self, chave):
        tela = self.telas[chave]
        tela.atualizar()          # POLIMORFISMO: cada tela recarrega seus dados
        tela.tkraise()            # traz a tela para a frente
        self.titulo.configure(text=tela.titulo)
        self.subtitulo.configure(text=tela.subtitulo)
        for nome, botao in self.botoes_menu.items():
            botao.configure(style="MenuAtivo.TButton" if nome == chave else "Menu.TButton")
        self.status.configure(text=self.repositorio.descricao(),
                              foreground=CORES["texto_suave"])

    def notificar(self, mensagem):
        """Mostra uma mensagem verde na barra de status (some depois de 5 s)."""
        self.status.configure(text=f"✓ {mensagem}  ·  salvo no banco",
                              foreground=CORES["sucesso"])
        if self._aviso_agendado:
            self.after_cancel(self._aviso_agendado)
        self._aviso_agendado = self.after(5000, self._limpar_aviso)

    def _limpar_aviso(self):
        self._aviso_agendado = None
        self.status.configure(text=self.repositorio.descricao(),
                              foreground=CORES["texto_suave"])

    def sair(self):
        self.repositorio.fechar()
        self.destroy()
