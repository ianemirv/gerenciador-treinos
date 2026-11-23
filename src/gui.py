"""Ponto de entrada da interface gráfica (nível 4).

Rode com:  python src/gui.py
Usa o mesmo banco SQLite do menu do terminal (treinos.db).
"""

import sys

from repository.banco import RepositorioSQLite
from ui.gui.janela_principal import JanelaPrincipal


def deixar_nitido_no_windows():
    """Sem isso, o Windows estica a janela e as letras ficam borradas."""
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except (AttributeError, OSError):
            pass


def main():
    deixar_nitido_no_windows()
    repositorio = RepositorioSQLite()   # abre (ou cria) o treinos.db e carrega os dados
    janela = JanelaPrincipal(repositorio)
    janela.mainloop()


if __name__ == "__main__":
    main()
