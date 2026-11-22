"""Fixtures usadas por vários arquivos de teste.

O fixture "repo" roda cada teste DUAS vezes: uma com o RepositorioMemoria
(nível 2) e outra com o RepositorioSQLite (nível 3), num banco temporário.
Assim garantimos que os dois se comportam igual.
"""

import pytest

from repository.banco import RepositorioSQLite
from repository.repositorio_memoria import RepositorioMemoria


@pytest.fixture(params=["memoria", "sqlite"])
def repo(request, tmp_path):
    if request.param == "memoria":
        yield RepositorioMemoria()
    else:
        repositorio = RepositorioSQLite(tmp_path / "teste.db")
        yield repositorio
        repositorio.fechar()


@pytest.fixture
def caminho_banco(tmp_path):
    """Caminho de um banco temporário (o pytest apaga depois do teste)."""
    return tmp_path / "treinos_teste.db"
