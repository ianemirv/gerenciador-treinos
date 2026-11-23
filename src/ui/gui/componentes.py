"""Componentes reutilizados por várias telas.

- Tabela: uma tabela (Treeview) com barra de rolagem que guarda o objeto
  de cada linha, assim a tela pega direto o Aluno/Ficha/Sessão selecionado.
- Seletor: uma caixa de escolha (Combobox) de objetos, ex.: escolher o aluno.
- JanelaFormulario: janela de cadastro/edição com campos e botão Salvar.
- GraficoBarras: gráfico de barras desenhado num Canvas.
- Funções de mensagem: erro, info e confirmar (janelas de aviso).
"""

import tkinter as tk
from tkinter import messagebox, ttk

from ui.gui.estilos import CORES, FONTES


# =========================================================================
# Mensagens em janelas
# =========================================================================
def erro(master, mensagem):
    messagebox.showerror("Atenção", str(mensagem), parent=master)


def info(master, mensagem, titulo="Pronto!"):
    messagebox.showinfo(titulo, mensagem, parent=master)


def confirmar(master, mensagem):
    return messagebox.askyesno("Confirmar", mensagem, parent=master)


def criar_cartao(master, titulo=None, padding=16):
    """Caixa branca com um título opcional. Devolve o frame do cartão."""
    cartao = ttk.Frame(master, style="Cartao.TFrame", padding=padding)
    if titulo:
        ttk.Label(cartao, text=titulo, style="CartaoTitulo.TLabel").pack(anchor="w", pady=(0, 10))
    return cartao


# =========================================================================
# Tabela
# =========================================================================
class Tabela(ttk.Frame):
    """colunas: lista de (id, título, largura, alinhamento "w"/"center"/"e")."""

    def __init__(self, master, colunas, altura=10):
        super().__init__(master, style="Cartao.TFrame")
        ids = [coluna[0] for coluna in colunas]
        self.arvore = ttk.Treeview(self, columns=ids, show="headings",
                                   height=altura, selectmode="browse")
        for id_coluna, titulo, largura, alinhamento in colunas:
            self.arvore.heading(id_coluna, text=titulo, anchor=alinhamento)
            self.arvore.column(id_coluna, width=largura, minwidth=40, anchor=alinhamento,
                               stretch=True)
        rolagem = ttk.Scrollbar(self, orient="vertical", command=self.arvore.yview)
        self.arvore.configure(yscrollcommand=rolagem.set)
        self.arvore.pack(side="left", fill="both", expand=True)
        rolagem.pack(side="right", fill="y")

        # Linhas listradas e cores por tipo de exercício
        self.arvore.tag_configure("impar", background="#F9FAFB")
        for tipo in ("musculacao", "cardio", "isometrico"):
            self.arvore.tag_configure(tipo, background=CORES[tipo])
        self._objetos = {}   # id da linha -> objeto mostrado nela

    def limpar(self):
        self.arvore.delete(*self.arvore.get_children())
        self._objetos.clear()

    def adicionar(self, valores, objeto, tag=None):
        if tag is None:
            tag = "impar" if len(self._objetos) % 2 else "par"
        iid = self.arvore.insert("", "end", values=valores, tags=(tag,))
        self._objetos[iid] = objeto

    @property
    def selecionado(self):
        """Objeto da linha selecionada (ou None)."""
        selecao = self.arvore.selection()
        return self._objetos.get(selecao[0]) if selecao else None

    def selecionar(self, objeto):
        for iid, item in self._objetos.items():
            if item is objeto:
                self.arvore.selection_set(iid)
                self.arvore.see(iid)
                return

    def ao_selecionar(self, funcao):
        self.arvore.bind("<<TreeviewSelect>>", lambda _evento: funcao())

    def ao_duplo_clique(self, funcao):
        self.arvore.bind("<Double-1>", lambda _evento: funcao())


# =========================================================================
# Seletor (Combobox de objetos)
# =========================================================================
class Seletor(ttk.Frame):
    """Caixa para escolher um objeto. "formatar" transforma o objeto em texto."""

    def __init__(self, master, rotulo, formatar, ao_mudar=None, largura=32, estilo_fundo=""):
        super().__init__(master, style=estilo_fundo or "TFrame")
        estilo_rotulo = "Cartao.TLabel" if estilo_fundo == "Cartao.TFrame" else "TLabel"
        ttk.Label(self, text=rotulo, style=estilo_rotulo,
                  font=FONTES["negrito"]).pack(side="left", padx=(0, 8))
        self.caixa = ttk.Combobox(self, state="readonly", width=largura)
        self.caixa.pack(side="left")
        self.formatar = formatar
        self.itens = []
        if ao_mudar:
            self.caixa.bind("<<ComboboxSelected>>", lambda _evento: ao_mudar())

    def definir_itens(self, itens):
        """Troca a lista, mantendo o item que estava escolhido (se ainda existir)."""
        anterior = self.selecionado
        self.itens = list(itens)
        self.caixa["values"] = [self.formatar(item) for item in self.itens]
        if anterior in self.itens:
            self.caixa.current(self.itens.index(anterior))
        elif self.itens:
            self.caixa.current(0)
        else:
            self.caixa.set("")

    def escolher(self, item):
        if item in self.itens:
            self.caixa.current(self.itens.index(item))

    @property
    def selecionado(self):
        indice = self.caixa.current()
        return self.itens[indice] if 0 <= indice < len(self.itens) else None


# =========================================================================
# Janela de formulário (cadastrar / editar)
# =========================================================================
class JanelaFormulario(tk.Toplevel):
    """Janela que abre por cima da principal com campos e botões.

    campos: lista de (chave, rótulo, valor inicial) ou
            (chave, rótulo, valor inicial, lista de opções) para uma caixa de escolha.
    ao_salvar(valores): recebe {chave: texto}. Se lançar ValueError, a mensagem
    aparece numa janela de erro e o formulário continua aberto para corrigir.
    """

    def __init__(self, master, titulo, campos, ao_salvar, subtitulo="", texto_botao="Salvar"):
        super().__init__(master)
        self.title(titulo)
        self.configure(background=CORES["cartao"])
        self.resizable(False, False)
        self.transient(master.winfo_toplevel())   # fica sempre na frente da principal
        self.ao_salvar = ao_salvar
        self.variaveis = {}

        corpo = ttk.Frame(self, style="Cartao.TFrame", padding=24)
        corpo.pack(fill="both", expand=True)
        ttk.Label(corpo, text=titulo, style="CartaoTitulo.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w")
        if subtitulo:
            ttk.Label(corpo, text=subtitulo, style="CartaoSuave.TLabel", wraplength=340).grid(
                row=1, column=0, columnspan=2, sticky="w", pady=(2, 0))

        primeiro = None
        for linha, campo in enumerate(campos, start=2):
            chave, rotulo, valor = campo[:3]
            opcoes = campo[3] if len(campo) > 3 else None
            ttk.Label(corpo, text=rotulo, style="Cartao.TLabel").grid(
                row=linha, column=0, sticky="w", pady=6, padx=(0, 12))
            variavel = tk.StringVar(value="" if valor is None else str(valor))
            if opcoes is not None:
                widget = ttk.Combobox(corpo, textvariable=variavel, values=opcoes,
                                      state="readonly", width=30)
            else:
                widget = ttk.Entry(corpo, textvariable=variavel, width=32)
            widget.grid(row=linha, column=1, sticky="ew", pady=6)
            self.variaveis[chave] = variavel
            primeiro = primeiro or widget

        botoes = ttk.Frame(corpo, style="Cartao.TFrame")
        botoes.grid(row=len(campos) + 2, column=0, columnspan=2, sticky="e", pady=(18, 0))
        ttk.Button(botoes, text="Cancelar", style="Secundario.TButton",
                   command=self.destroy).pack(side="left", padx=(0, 8))
        ttk.Button(botoes, text=texto_botao, style="Primario.TButton",
                   command=self.salvar).pack(side="left")

        self.bind("<Return>", lambda _evento: self.salvar())
        self.bind("<Escape>", lambda _evento: self.destroy())
        self._centralizar(master.winfo_toplevel())
        self.after(50, self._bloquear_janela_de_tras)
        if primeiro is not None:
            primeiro.focus_set()

    def _bloquear_janela_de_tras(self):
        # grab_set: enquanto este formulário está aberto, não dá para clicar na principal
        try:
            self.grab_set()
        except tk.TclError:
            pass

    def _centralizar(self, principal):
        self.update_idletasks()
        x = principal.winfo_rootx() + (principal.winfo_width() - self.winfo_reqwidth()) // 2
        y = principal.winfo_rooty() + (principal.winfo_height() - self.winfo_reqheight()) // 3
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    def salvar(self):
        valores = {chave: variavel.get().strip() for chave, variavel in self.variaveis.items()}
        try:
            self.ao_salvar(valores)
        except (ValueError, TypeError) as problema:
            erro(self, problema)     # mostra o erro e deixa o usuário corrigir
            return
        self.destroy()


# =========================================================================
# Gráfico de barras
# =========================================================================
class GraficoBarras(tk.Canvas):
    """Gráfico desenhado à mão no Canvas: uma barra por valor.

    Se com_linha=True, também liga o topo das barras com uma linha
    (bom para ver a evolução).
    """

    MARGEM_ESQ, MARGEM_DIR, MARGEM_TOPO, MARGEM_BAIXO = 56, 20, 30, 44

    def __init__(self, master, altura=300, com_linha=False):
        super().__init__(master, height=altura, background=CORES["cartao"],
                         highlightthickness=0)
        self.com_linha = com_linha
        self.rotulos, self.valores, self.unidade = [], [], ""
        self.bind("<Configure>", lambda _evento: self._desenhar())

    def mostrar(self, rotulos, valores, unidade=""):
        self.rotulos, self.valores, self.unidade = list(rotulos), list(valores), unidade
        self._desenhar()

    def _desenhar(self):
        self.delete("all")
        largura, altura = self.winfo_width(), self.winfo_height()
        if largura < 50:
            return
        if not self.valores:
            self.create_text(largura / 2, altura / 2, text="Ainda não há dados para mostrar.",
                             fill=CORES["texto_suave"], font=FONTES["normal"])
            return

        esq, dir_, topo = self.MARGEM_ESQ, largura - self.MARGEM_DIR, self.MARGEM_TOPO
        base = altura - self.MARGEM_BAIXO
        maior = max(self.valores) or 1

        # Linhas de grade com os valores do eixo
        for i in range(5):
            y = base - (base - topo) * i / 4
            self.create_line(esq, y, dir_, y, fill=CORES["borda"])
            self.create_text(esq - 8, y, text=f"{maior * i / 4:g}", anchor="e",
                             fill=CORES["texto_suave"], font=FONTES["pequena"])

        espaco = (dir_ - esq) / len(self.valores)
        largura_barra = min(60, espaco * 0.6)
        topos = []
        for i, (rotulo, valor) in enumerate(zip(self.rotulos, self.valores)):
            centro = esq + espaco * (i + 0.5)
            y = base - (base - topo) * valor / maior
            self.create_rectangle(centro - largura_barra / 2, y, centro + largura_barra / 2,
                                  base, fill=CORES["destaque"], outline="")
            self.create_text(centro, y - 10, text=f"{valor:g} {self.unidade}".strip(),
                             fill=CORES["texto"], font=FONTES["negrito"])
            self.create_text(centro, base + 16, text=rotulo, fill=CORES["texto_suave"],
                             font=FONTES["pequena"])
            topos.append((centro, y))

        if self.com_linha and len(topos) > 1:
            self.create_line(*[coord for ponto in topos for coord in ponto],
                             fill=CORES["lateral"], width=2, smooth=True)
            for x, y in topos:
                self.create_oval(x - 4, y - 4, x + 4, y + 4, fill=CORES["lateral"], outline="")
        self.create_line(esq, base, dir_, base, fill=CORES["texto_suave"])
