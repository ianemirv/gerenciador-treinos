"""TelaBase: classe mãe (abstrata) de todas as telas da interface.

HERANÇA: cada tela (Início, Alunos, Instrutores...) herda de TelaBase.
POLIMORFISMO: a janela principal chama tela.atualizar() sem saber qual
tela é; cada uma recarrega os próprios dados do seu jeito.
"""

from abc import ABC, abstractmethod
from tkinter import ttk


class TelaBase(ttk.Frame, ABC):
    titulo = ""        # aparece no topo da janela
    subtitulo = ""

    def __init__(self, master, app):
        super().__init__(master, padding=(28, 8, 28, 20))
        self.app = app                     # a JanelaPrincipal
        self.ctrl = app.controlador        # ControladorGUI: valida e chama o repositório
        self.montar()

    @abstractmethod
    def montar(self):
        """Cria os widgets da tela (chamado uma vez)."""

    @abstractmethod
    def atualizar(self):
        """Recarrega os dados mostrados (chamado toda vez que a tela aparece)."""

    # Atalhos usados pelas telas filhas
    def avisar(self, mensagem):
        self.app.notificar(mensagem)
