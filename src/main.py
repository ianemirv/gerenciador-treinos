"""Ponto de entrada do Gerenciador de Treinos.

Rode com:  python src/main.py
Nível 2: menu no terminal, com os dados guardados só na memória.
"""

from repository.repositorio_memoria import RepositorioMemoria
from ui.menu_terminal import MenuTerminal


def main():
    menu = MenuTerminal(RepositorioMemoria())
    try:
        menu.executar()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C ou fim da entrada: fecha sem mostrar erro.
        print("\n\nPrograma encerrado.")


if __name__ == "__main__":
    main()
