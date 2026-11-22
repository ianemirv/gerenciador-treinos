"""Ponto de entrada do Gerenciador de Treinos.

Rode com:  python src/main.py
Nível 3: menu no terminal com os dados salvos no banco SQLite (treinos.db).
"""

from repository.banco import RepositorioSQLite
from ui.menu_terminal import MenuTerminal


def main():
    repositorio = RepositorioSQLite()   # abre (ou cria) o treinos.db e carrega os dados
    menu = MenuTerminal(repositorio)
    try:
        menu.executar()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C ou fim da entrada: fecha sem mostrar erro.
        # Nada se perde, porque cada alteração já foi salva no banco.
        print("\n\nPrograma encerrado. Os dados continuam salvos no banco.")
    finally:
        repositorio.fechar()


if __name__ == "__main__":
    main()
