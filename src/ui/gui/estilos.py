"""Estilos personalizados da interface: cores, fontes e o visual dos widgets.

Usamos o ttk (que já vem com o Tkinter) no tema "clam", que deixa trocar
as cores de quase tudo. Cada estilo tem um nome, por exemplo
"Primario.TButton", e os widgets escolhem o estilo com style="...".
"""

from tkinter import font as tkfont
from tkinter import ttk

# Paleta de cores do app
CORES = {
    "fundo": "#F3F4F6",          # fundo das telas (cinza bem claro)
    "cartao": "#FFFFFF",         # caixas brancas
    "lateral": "#111827",        # menu lateral (quase preto)
    "lateral_hover": "#1F2937",
    "lateral_texto": "#9CA3AF",
    "destaque": "#F97316",       # laranja: cor principal do app
    "destaque_escuro": "#EA580C",
    "destaque_claro": "#FFEDD5",
    "texto": "#1F2937",
    "texto_suave": "#6B7280",
    "borda": "#E5E7EB",
    "sucesso": "#16A34A",
    "perigo": "#DC2626",
    "perigo_escuro": "#B91C1C",
    # uma cor por tipo de exercício (usadas nas linhas das tabelas)
    "musculacao": "#FFF7ED",
    "cardio": "#ECFDF5",
    "isometrico": "#EFF6FF",
}

FAMILIA = "Segoe UI"   # fonte padrão do Windows; em outro sistema o Tk usa uma parecida

FONTES = {
    "normal": (FAMILIA, 10),
    "negrito": (FAMILIA, 10, "bold"),
    "pequena": (FAMILIA, 9),
    "titulo": (FAMILIA, 20, "bold"),
    "subtitulo": (FAMILIA, 12, "bold"),
    "numero": (FAMILIA, 26, "bold"),
    "logo": (FAMILIA, 15, "bold"),
    "menu": (FAMILIA, 11),
}


def aplicar_estilos(janela):
    """Configura todos os estilos. É chamada uma vez, ao abrir a janela."""
    janela.configure(background=CORES["fundo"])

    # Fonte padrão de todos os widgets
    for nome in ("TkDefaultFont", "TkTextFont", "TkHeadingFont", "TkMenuFont"):
        tkfont.nametofont(nome).configure(family=FAMILIA, size=10)
    janela.option_add("*TCombobox*Listbox.font", FONTES["normal"])
    janela.option_add("*TCombobox*Listbox.selectBackground", CORES["destaque"])

    estilo = ttk.Style(janela)
    estilo.theme_use("clam")

    # ---------- base ----------
    estilo.configure(".", background=CORES["fundo"], foreground=CORES["texto"],
                     font=FONTES["normal"])
    estilo.configure("TFrame", background=CORES["fundo"])
    estilo.configure("Cartao.TFrame", background=CORES["cartao"])
    estilo.configure("Lateral.TFrame", background=CORES["lateral"])

    # ---------- textos ----------
    estilo.configure("TLabel", background=CORES["fundo"])
    estilo.configure("Titulo.TLabel", font=FONTES["titulo"])
    estilo.configure("Suave.TLabel", foreground=CORES["texto_suave"])
    estilo.configure("Cartao.TLabel", background=CORES["cartao"])
    estilo.configure("CartaoTitulo.TLabel", background=CORES["cartao"],
                     font=FONTES["subtitulo"])
    estilo.configure("CartaoSuave.TLabel", background=CORES["cartao"],
                     foreground=CORES["texto_suave"])
    estilo.configure("CartaoNumero.TLabel", background=CORES["cartao"],
                     foreground=CORES["destaque"], font=FONTES["numero"])
    estilo.configure("Logo.TLabel", background=CORES["lateral"], foreground="white",
                     font=FONTES["logo"])
    estilo.configure("LateralSuave.TLabel", background=CORES["lateral"],
                     foreground=CORES["lateral_texto"], font=FONTES["pequena"])
    estilo.configure("Status.TLabel", background=CORES["cartao"],
                     foreground=CORES["texto_suave"], padding=(16, 6))

    # ---------- botões ----------
    estilo.configure("TButton", padding=(14, 7), borderwidth=0, relief="flat",
                     font=FONTES["negrito"])
    _botao(estilo, "Primario.TButton", CORES["destaque"], CORES["destaque_escuro"], "white")
    _botao(estilo, "Perigo.TButton", CORES["perigo"], CORES["perigo_escuro"], "white")
    _botao(estilo, "Secundario.TButton", "#E5E7EB", "#D1D5DB", CORES["texto"])

    # Botões do menu lateral: sem borda, alinhados à esquerda
    _botao(estilo, "Menu.TButton", CORES["lateral"], CORES["lateral_hover"],
           CORES["lateral_texto"])
    estilo.configure("Menu.TButton", anchor="w", padding=(24, 11), font=FONTES["menu"])
    estilo.map("Menu.TButton", foreground=[("active", "white")])
    _botao(estilo, "MenuAtivo.TButton", CORES["lateral_hover"], CORES["lateral_hover"],
           CORES["destaque"])
    estilo.configure("MenuAtivo.TButton", anchor="w", padding=(24, 11),
                     font=(FAMILIA, 11, "bold"))

    # ---------- campos ----------
    for tipo in ("TEntry", "TCombobox", "TSpinbox"):
        estilo.configure(tipo, fieldbackground="white", padding=6,
                         bordercolor=CORES["borda"], lightcolor=CORES["borda"],
                         darkcolor=CORES["borda"], arrowcolor=CORES["texto_suave"])
        estilo.map(tipo,
                   bordercolor=[("focus", CORES["destaque"])],
                   lightcolor=[("focus", CORES["destaque"])],
                   fieldbackground=[("readonly", "white"), ("disabled", CORES["fundo"])])
    estilo.map("TCombobox", selectbackground=[("readonly", "white")],
               selectforeground=[("readonly", CORES["texto"])])
    estilo.configure("Cartao.TCheckbutton", background=CORES["cartao"],
                     indicatorbackground="white", indicatorforeground=CORES["destaque"])
    estilo.map("Cartao.TCheckbutton", background=[("active", CORES["cartao"])])

    # ---------- tabelas (Treeview) ----------
    altura_linha = tkfont.Font(font=FONTES["normal"]).metrics("linespace") + 12
    estilo.configure("Treeview", background="white", fieldbackground="white",
                     foreground=CORES["texto"], rowheight=altura_linha, borderwidth=0)
    estilo.map("Treeview",
               background=[("selected", CORES["destaque_claro"])],
               foreground=[("selected", CORES["texto"])])
    estilo.configure("Treeview.Heading", background=CORES["lateral"], foreground="white",
                     font=FONTES["negrito"], relief="flat", padding=(8, 6))
    estilo.map("Treeview.Heading", background=[("active", CORES["lateral_hover"])])
    estilo.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])  # sem borda

    # ---------- abas (Notebook) ----------
    estilo.configure("TNotebook", background=CORES["fundo"], borderwidth=0)
    estilo.configure("TNotebook.Tab", padding=(18, 8), background="#E5E7EB",
                     foreground=CORES["texto_suave"], font=FONTES["negrito"], borderwidth=0)
    estilo.map("TNotebook.Tab",
               background=[("selected", CORES["cartao"])],
               foreground=[("selected", CORES["destaque"])])

    estilo.configure("Vertical.TScrollbar", background="#E5E7EB", troughcolor="white",
                     bordercolor="white", arrowcolor=CORES["texto_suave"])
    return estilo


def _botao(estilo, nome, cor, cor_hover, cor_texto):
    """Cria um estilo de botão com cor normal, cor ao passar o mouse e desativado."""
    estilo.configure(nome, background=cor, foreground=cor_texto, bordercolor=cor,
                     lightcolor=cor, darkcolor=cor, focuscolor=cor)
    estilo.map(nome,
               background=[("disabled", "#E5E7EB"), ("pressed", cor_hover), ("active", cor_hover)],
               bordercolor=[("disabled", "#E5E7EB"), ("pressed", cor_hover), ("active", cor_hover)],
               lightcolor=[("disabled", "#E5E7EB"), ("pressed", cor_hover), ("active", cor_hover)],
               darkcolor=[("disabled", "#E5E7EB"), ("pressed", cor_hover), ("active", cor_hover)],
               foreground=[("disabled", "#9CA3AF")])


def cor_do_imc(faixa):
    """Cor usada no relatório de IMC para cada faixa."""
    return {
        "Abaixo do peso": "#0EA5E9",
        "Peso normal": CORES["sucesso"],
        "Sobrepeso": "#F59E0B",
        "Obesidade": CORES["perigo"],
    }.get(faixa, CORES["texto"])
