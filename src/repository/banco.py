"""RepositorioSQLite: guarda tudo num banco de dados SQLite (nível 3).

Como funciona:
- Ao abrir, cria as tabelas (se ainda não existirem) e CARREGA tudo do banco,
  montando de novo os objetos (Aluno, FichaTreino, SessaoTreino...).
- HERANÇA: a classe herda do RepositorioMemoria. Cada método que altera os
  dados chama a versão da classe mãe com super() (que valida e altera os
  objetos) e depois executa o SQL correspondente (INSERT, UPDATE ou DELETE).
- Cada alteração é salva na hora (commit), então nada se perde se o
  programa fechar de repente.

O sqlite3 já vem com o Python, não precisa instalar nada.
"""

import sqlite3
from datetime import date
from pathlib import Path

from models.exercicio import ExercicioCardio, ExercicioIsometrico, ExercicioMusculacao
from models.ficha_treino import FichaTreino
from models.pessoa import Aluno, Instrutor
from models.sessao_treino import SessaoTreino
from repository.repositorio_memoria import RepositorioMemoria

# Arquivo do banco: fica na pasta principal do projeto (gerenciador-treinos/treinos.db)
CAMINHO_PADRAO = Path(__file__).resolve().parents[2] / "treinos.db"

TABELAS = ["instrutores", "alunos", "fichas", "exercicios", "sessoes", "registros"]

CRIAR_TABELAS = """
CREATE TABLE IF NOT EXISTS instrutores (
    cpf     TEXT PRIMARY KEY,
    nome    TEXT NOT NULL,
    idade   INTEGER NOT NULL,
    cref    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS alunos (
    cpf            TEXT PRIMARY KEY,
    nome           TEXT NOT NULL,
    idade          INTEGER NOT NULL,
    peso_kg        REAL NOT NULL,
    altura_m       REAL NOT NULL,
    -- associação: o instrutor que acompanha o aluno (pode ficar vazio)
    instrutor_cpf  TEXT REFERENCES instrutores(cpf) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS fichas (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_cpf  TEXT NOT NULL REFERENCES alunos(cpf) ON DELETE CASCADE,
    nome       TEXT NOT NULL
);

-- Os 3 tipos de exercício ficam numa tabela só; a coluna "tipo" diz qual
-- classe criar ao carregar, e cada tipo usa só as suas colunas.
CREATE TABLE IF NOT EXISTS exercicios (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ficha_id        INTEGER NOT NULL REFERENCES fichas(id) ON DELETE CASCADE,
    tipo            TEXT NOT NULL CHECK (tipo IN ('musculacao', 'cardio', 'isometrico')),
    nome            TEXT NOT NULL,
    grupo_muscular  TEXT NOT NULL,
    series          INTEGER,
    repeticoes      INTEGER,
    carga_kg        REAL,
    duracao_min     REAL,
    distancia_km    REAL,
    tempo_s         REAL,
    -- 0 = saiu da ficha, mas continua no histórico das sessões antigas
    ativo           INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS sessoes (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_cpf    TEXT NOT NULL REFERENCES alunos(cpf) ON DELETE CASCADE,
    ficha_id     INTEGER NOT NULL REFERENCES fichas(id),
    data         TEXT NOT NULL,          -- formato AAAA-MM-DD
    duracao_min  REAL NOT NULL,
    observacao   TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS registros (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    sessao_id     INTEGER NOT NULL REFERENCES sessoes(id) ON DELETE CASCADE,
    exercicio_id  INTEGER NOT NULL REFERENCES exercicios(id) ON DELETE CASCADE,
    series        INTEGER NOT NULL,
    repeticoes    INTEGER NOT NULL,
    carga_kg      REAL NOT NULL
);
"""


class RepositorioSQLite(RepositorioMemoria):
    """HERANÇA: é um RepositorioMemoria que também grava tudo no SQLite."""

    def __init__(self, caminho=CAMINHO_PADRAO):
        super().__init__()
        self.caminho = str(caminho)
        self.conexao = sqlite3.connect(self.caminho)
        self.conexao.row_factory = sqlite3.Row          # acessar colunas pelo nome
        self.conexao.execute("PRAGMA foreign_keys = ON")  # liga o ON DELETE CASCADE
        self.conexao.executescript(CRIAR_TABELAS)
        # Fichas, exercícios e sessões não têm um "id" nos modelos.
        # Este dicionário guarda: objeto -> id da linha no banco.
        self._ids = {}
        self._carregar()

    def descricao(self):
        return f"Todos os dados estão salvos no banco {Path(self.caminho).name}."

    def fechar(self):
        self.conexao.close()

    # =====================================================================
    # Carregar: lê as tabelas e monta os objetos de novo
    # =====================================================================
    def _carregar(self):
        sql = self.conexao.execute

        # super() = métodos do RepositorioMemoria: só montam os objetos,
        # sem gravar de novo no banco.
        for linha in sql("SELECT * FROM instrutores ORDER BY rowid"):
            super().adicionar_instrutor(
                Instrutor(linha["nome"], linha["cpf"], linha["idade"], linha["cref"]))

        for linha in sql("SELECT * FROM alunos ORDER BY rowid"):
            aluno = Aluno(linha["nome"], linha["cpf"], linha["idade"],
                          linha["peso_kg"], linha["altura_m"])
            super().adicionar_aluno(aluno)
            if linha["instrutor_cpf"] is not None:
                super().vincular(self.buscar_instrutor(linha["instrutor_cpf"]), aluno)

        fichas = {}
        for linha in sql("SELECT * FROM fichas ORDER BY id"):
            ficha = FichaTreino(linha["nome"])
            self.buscar_aluno(linha["aluno_cpf"]).adicionar_ficha(ficha)
            fichas[linha["id"]] = ficha
            self._ids[ficha] = linha["id"]

        exercicios = {}
        for linha in sql("SELECT * FROM exercicios ORDER BY id"):
            exercicio = self._montar_exercicio(fichas[linha["ficha_id"]], linha)
            exercicios[linha["id"]] = exercicio
            self._ids[exercicio] = linha["id"]

        for linha in sql("SELECT * FROM sessoes ORDER BY id"):
            sessao = SessaoTreino(date.fromisoformat(linha["data"]),
                                  fichas[linha["ficha_id"]],
                                  linha["duracao_min"], linha["observacao"])
            registros = sql("SELECT * FROM registros WHERE sessao_id = ? ORDER BY id",
                            (linha["id"],))
            for registro in registros:
                sessao.adicionar_registro(exercicios[registro["exercicio_id"]],
                                          registro["series"], registro["repeticoes"],
                                          registro["carga_kg"])
            self.buscar_aluno(linha["aluno_cpf"]).registrar_sessao(sessao)
            self._ids[sessao] = linha["id"]

    @staticmethod
    def _montar_exercicio(ficha, linha):
        """Cria o objeto certo a partir da coluna "tipo" da linha."""
        tipo = linha["tipo"]
        if tipo == "musculacao":
            dados = (linha["nome"], linha["grupo_muscular"], linha["series"],
                     linha["repeticoes"], linha["carga_kg"])
            criar_na_ficha, classe = ficha.adicionar_musculacao, ExercicioMusculacao
        elif tipo == "cardio":
            dados = (linha["nome"], linha["duracao_min"], linha["distancia_km"])
            criar_na_ficha, classe = ficha.adicionar_cardio, ExercicioCardio
        else:
            dados = (linha["nome"], linha["grupo_muscular"], linha["series"],
                     linha["tempo_s"])
            criar_na_ficha, classe = ficha.adicionar_isometrico, ExercicioIsometrico

        if linha["ativo"]:
            return criar_na_ficha(*dados)  # COMPOSIÇÃO: a ficha cria o exercício
        # Exercício que saiu da ficha: existe só para o histórico das sessões.
        return classe(*dados)

    # =====================================================================
    # Alunos
    # =====================================================================
    def adicionar_aluno(self, aluno):
        super().adicionar_aluno(aluno)
        with self.conexao:  # "with" faz o commit (ou desfaz tudo se der erro)
            self.conexao.execute(
                "INSERT INTO alunos (cpf, nome, idade, peso_kg, altura_m) "
                "VALUES (?, ?, ?, ?, ?)",
                (aluno.cpf, aluno.nome, aluno.idade, aluno.peso_kg, aluno.altura_m))

    def atualizar_aluno(self, aluno):
        super().atualizar_aluno(aluno)
        with self.conexao:
            self.conexao.execute(
                "UPDATE alunos SET nome = ?, idade = ?, peso_kg = ?, altura_m = ? "
                "WHERE cpf = ?",
                (aluno.nome, aluno.idade, aluno.peso_kg, aluno.altura_m, aluno.cpf))

    def remover_aluno(self, cpf):
        aluno = super().remover_aluno(cpf)
        with self.conexao:
            # ON DELETE CASCADE apaga junto as fichas, exercícios, sessões e registros.
            self.conexao.execute("DELETE FROM alunos WHERE cpf = ?", (aluno.cpf,))
        return aluno

    # =====================================================================
    # Instrutores
    # =====================================================================
    def adicionar_instrutor(self, instrutor):
        super().adicionar_instrutor(instrutor)
        with self.conexao:
            self.conexao.execute(
                "INSERT INTO instrutores (cpf, nome, idade, cref) VALUES (?, ?, ?, ?)",
                (instrutor.cpf, instrutor.nome, instrutor.idade, instrutor.cref))

    def remover_instrutor(self, cpf):
        instrutor = super().remover_instrutor(cpf)
        with self.conexao:
            # ON DELETE SET NULL: os alunos continuam, só ficam sem instrutor.
            self.conexao.execute("DELETE FROM instrutores WHERE cpf = ?", (instrutor.cpf,))
        return instrutor

    def vincular(self, instrutor, aluno):
        super().vincular(instrutor, aluno)
        with self.conexao:
            self.conexao.execute("UPDATE alunos SET instrutor_cpf = ? WHERE cpf = ?",
                                 (instrutor.cpf, aluno.cpf))

    def desvincular(self, instrutor, aluno):
        super().desvincular(instrutor, aluno)
        with self.conexao:
            self.conexao.execute("UPDATE alunos SET instrutor_cpf = NULL WHERE cpf = ?",
                                 (aluno.cpf,))

    # =====================================================================
    # Fichas e exercícios
    # =====================================================================
    def adicionar_ficha(self, aluno, ficha):
        super().adicionar_ficha(aluno, ficha)
        with self.conexao:
            cursor = self.conexao.execute(
                "INSERT INTO fichas (aluno_cpf, nome) VALUES (?, ?)", (aluno.cpf, ficha.nome))
            self._ids[ficha] = cursor.lastrowid   # id que o banco gerou
            # A ficha é salva junto com os exercícios que já tiver (composição).
            for exercicio in ficha.exercicios:
                self._inserir_exercicio(ficha, exercicio)

    def remover_ficha(self, aluno, ficha):
        super().remover_ficha(aluno, ficha)
        with self.conexao:
            self.conexao.execute("DELETE FROM fichas WHERE id = ?", (self._ids.pop(ficha),))

    def salvar_exercicio(self, ficha, exercicio):
        super().salvar_exercicio(ficha, exercicio)
        with self.conexao:
            self._inserir_exercicio(ficha, exercicio)

    def remover_exercicio(self, ficha, exercicio):
        super().remover_exercicio(ficha, exercicio)
        id_exercicio = self._ids[exercicio]
        with self.conexao:
            usado = self.conexao.execute(
                "SELECT 1 FROM registros WHERE exercicio_id = ? LIMIT 1",
                (id_exercicio,)).fetchone()
            if usado:
                # Já aparece em sessões: sai da ficha, mas fica no histórico.
                self.conexao.execute("UPDATE exercicios SET ativo = 0 WHERE id = ?",
                                     (id_exercicio,))
            else:
                self.conexao.execute("DELETE FROM exercicios WHERE id = ?", (id_exercicio,))
                del self._ids[exercicio]

    def _inserir_exercicio(self, ficha, exercicio):
        colunas = {
            "ficha_id": self._ids[ficha], "nome": exercicio.nome,
            "grupo_muscular": exercicio.grupo_muscular,
            "series": None, "repeticoes": None, "carga_kg": None,
            "duracao_min": None, "distancia_km": None, "tempo_s": None,
        }
        # Cada tipo de exercício preenche só as suas colunas.
        if isinstance(exercicio, ExercicioMusculacao):
            colunas.update(tipo="musculacao", series=exercicio.series,
                           repeticoes=exercicio.repeticoes, carga_kg=exercicio.carga_kg)
        elif isinstance(exercicio, ExercicioCardio):
            colunas.update(tipo="cardio", duracao_min=exercicio.duracao_min,
                           distancia_km=exercicio.distancia_km)
        else:
            colunas.update(tipo="isometrico", series=exercicio.series,
                           tempo_s=exercicio.tempo_s)
        cursor = self.conexao.execute(
            "INSERT INTO exercicios (ficha_id, tipo, nome, grupo_muscular, series, "
            "repeticoes, carga_kg, duracao_min, distancia_km, tempo_s) "
            "VALUES (:ficha_id, :tipo, :nome, :grupo_muscular, :series, "
            ":repeticoes, :carga_kg, :duracao_min, :distancia_km, :tempo_s)",
            colunas)
        self._ids[exercicio] = cursor.lastrowid

    # =====================================================================
    # Sessões
    # =====================================================================
    def registrar_sessao(self, aluno, sessao):
        super().registrar_sessao(aluno, sessao)
        with self.conexao:
            cursor = self.conexao.execute(
                "INSERT INTO sessoes (aluno_cpf, ficha_id, data, duracao_min, observacao) "
                "VALUES (?, ?, ?, ?, ?)",
                (aluno.cpf, self._ids[sessao.ficha], sessao.data.isoformat(),
                 sessao.duracao_min, sessao.observacao))
            self._ids[sessao] = cursor.lastrowid
            # Os registros são salvos junto com a sessão (composição).
            for registro in sessao.registros:
                self.conexao.execute(
                    "INSERT INTO registros (sessao_id, exercicio_id, series, repeticoes, "
                    "carga_kg) VALUES (?, ?, ?, ?, ?)",
                    (self._ids[sessao], self._ids[registro.exercicio], registro.series,
                     registro.repeticoes, registro.carga_kg))
