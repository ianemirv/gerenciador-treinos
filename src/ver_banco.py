"""Mostra o conteúdo de todas as tabelas do banco treinos.db.

Rode com:  python src/ver_banco.py
Serve para conferir o que o menu salvou (ex.: no vídeo do nível 3).
"""

import sqlite3

from repository.banco import CAMINHO_PADRAO, TABELAS


def mostrar_tabela(conexao, tabela):
    cursor = conexao.execute(f"SELECT * FROM {tabela}")
    colunas = [c[0] for c in cursor.description]
    linhas = [["" if v is None else str(v) for v in linha] for linha in cursor.fetchall()]

    print(f"\n=== {tabela} ({len(linhas)} linha(s)) ===")
    # Largura de cada coluna = maior texto da coluna (com limite de 22 caracteres)
    larguras = [min(22, max([len(c)] + [len(l[i]) for l in linhas]))
                for i, c in enumerate(colunas)]
    print("  ".join(c[:22].ljust(w) for c, w in zip(colunas, larguras)))
    print("  ".join("-" * w for w in larguras))
    for linha in linhas:
        print("  ".join(v[:22].ljust(w) for v, w in zip(linha, larguras)))


def main():
    if not CAMINHO_PADRAO.exists():
        print(f"O banco {CAMINHO_PADRAO.name} ainda não existe. Rode o menu primeiro.")
        return
    conexao = sqlite3.connect(CAMINHO_PADRAO)
    print(f"Banco: {CAMINHO_PADRAO}")
    for tabela in TABELAS:
        mostrar_tabela(conexao, tabela)
    conexao.close()


if __name__ == "__main__":
    main()
