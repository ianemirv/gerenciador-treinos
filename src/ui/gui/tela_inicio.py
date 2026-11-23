"""Tela inicial: resumo do que está cadastrado e atalhos."""

from tkinter import ttk

from ui.gui.componentes import criar_cartao, info
from ui.gui.tela_base import TelaBase


class TelaInicio(TelaBase):
    titulo = "Início"
    subtitulo = "Resumo da academia e atalhos rápidos"

    def montar(self):
        # Quatro cartões com os totais
        linha = ttk.Frame(self)
        linha.pack(fill="x")
        self.numeros = {}
        cartoes = [("alunos", "Alunos"), ("instrutores", "Instrutores"),
                   ("fichas", "Fichas de treino"), ("sessoes", "Sessões registradas")]
        for coluna, (chave, texto) in enumerate(cartoes):
            cartao = criar_cartao(linha, padding=20)
            cartao.grid(row=0, column=coluna, sticky="nsew", padx=(0 if coluna == 0 else 12, 0))
            linha.columnconfigure(coluna, weight=1)
            ttk.Label(cartao, text=texto, style="CartaoSuave.TLabel").pack(anchor="w")
            self.numeros[chave] = ttk.Label(cartao, text="0", style="CartaoNumero.TLabel")
            self.numeros[chave].pack(anchor="w")

        # Atalhos para as telas mais usadas
        atalhos = criar_cartao(self, "Começar", padding=20)
        atalhos.pack(fill="x", pady=(16, 0))
        botoes = ttk.Frame(atalhos, style="Cartao.TFrame")
        botoes.pack(anchor="w")
        for texto, tela in [("Cadastrar aluno", "alunos"), ("Montar ficha", "fichas"),
                            ("Registrar treino", "sessao"), ("Ver relatórios", "relatorios")]:
            ttk.Button(botoes, text=texto, style="Primario.TButton",
                       command=lambda t=tela: self.app.mostrar(t)).pack(side="left", padx=(0, 10))

        # Dados de exemplo
        exemplo = criar_cartao(self, "Dados de exemplo", padding=20)
        exemplo.pack(fill="x", pady=(16, 0))
        ttk.Label(exemplo, style="CartaoSuave.TLabel", wraplength=700, justify="left",
                  text="Cadastra a instrutora Carla, os alunos João e Maria, fichas com os três "
                       "tipos de exercício e várias sessões de treino do João, para ver os "
                       "relatórios funcionando.").pack(anchor="w", pady=(0, 12))
        ttk.Button(exemplo, text="Carregar dados de exemplo", style="Secundario.TButton",
                   command=self.carregar_exemplo).pack(anchor="w")

        # Onde os dados ficam
        banco = criar_cartao(self, "Banco de dados", padding=20)
        banco.pack(fill="x", pady=(16, 0))
        self.texto_banco = ttk.Label(banco, style="CartaoSuave.TLabel")
        self.texto_banco.pack(anchor="w")

    def atualizar(self):
        for chave, valor in self.ctrl.resumo().items():
            self.numeros[chave].configure(text=str(valor))
        self.texto_banco.configure(
            text=f"{self.ctrl.repo.descricao()} Cada alteração é salva na hora, "
                 "então os dados continuam aqui depois de fechar o programa.")

    def carregar_exemplo(self):
        if self.ctrl.carregar_exemplo():
            info(self, "Dados de exemplo carregados: 1 instrutora, 2 alunos, "
                       "fichas e 7 sessões de treino.")
            self.avisar("Dados de exemplo carregados")
        else:
            info(self, "Os dados de exemplo já foram carregados.", titulo="Aviso")
        self.atualizar()
