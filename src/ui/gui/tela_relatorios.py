"""Tela de relatórios: evolução de carga, volume por semana e IMC (com gráficos)."""

import tkinter as tk
from tkinter import ttk

from ui.gui.componentes import GraficoBarras, Seletor
from ui.gui.controlador import formatar_cpf
from ui.gui.estilos import CORES, FAMILIA, FONTES, cor_do_imc
from ui.gui.tela_base import TelaBase

# Faixas de IMC desenhadas na régua: (início, fim, nome)
FAIXAS_IMC = [(15, 18.5, "Abaixo do peso"), (18.5, 25, "Peso normal"),
              (25, 30, "Sobrepeso"), (30, 40, "Obesidade")]


class TelaRelatorios(TelaBase):
    titulo = "Relatórios"
    subtitulo = "Calculados pelo RelatorioEvolucao a partir das sessões do aluno"

    def montar(self):
        self.seletor = Seletor(self, "Aluno:", lambda a: f"{a.nome} ({formatar_cpf(a.cpf)})",
                               ao_mudar=self.atualizar_relatorios)
        self.seletor.pack(anchor="w", pady=(0, 14))

        abas = ttk.Notebook(self)
        abas.pack(fill="both", expand=True)

        # ---------- aba 1: evolução de carga ----------
        aba_carga = ttk.Frame(abas, style="Cartao.TFrame", padding=20)
        abas.add(aba_carga, text="Evolução de carga")
        self.seletor_exercicio = Seletor(aba_carga, "Exercício:", lambda nome: nome,
                                         ao_mudar=self.mostrar_carga, largura=24,
                                         estilo_fundo="Cartao.TFrame")
        self.seletor_exercicio.pack(anchor="w")
        self.variacao = ttk.Label(aba_carga, style="CartaoTitulo.TLabel")
        self.variacao.pack(anchor="w", pady=(12, 0))
        self.grafico_carga = GraficoBarras(aba_carga, com_linha=True)
        self.grafico_carga.pack(fill="both", expand=True, pady=(8, 0))

        # ---------- aba 2: volume por semana ----------
        aba_volume = ttk.Frame(abas, style="Cartao.TFrame", padding=20)
        abas.add(aba_volume, text="Volume por semana")
        ttk.Label(aba_volume, style="CartaoSuave.TLabel",
                  text="Soma de séries × repetições × carga de todas as sessões da semana"
                  ).pack(anchor="w")
        self.grafico_volume = GraficoBarras(aba_volume)
        self.grafico_volume.pack(fill="both", expand=True, pady=(8, 0))

        # ---------- aba 3: IMC ----------
        aba_imc = ttk.Frame(abas, style="Cartao.TFrame", padding=28)
        abas.add(aba_imc, text="IMC")
        self.imc_numero = tk.Label(aba_imc, font=(FAMILIA, 44, "bold"),
                                   background=CORES["cartao"])
        self.imc_numero.pack(anchor="w")
        self.imc_faixa = tk.Label(aba_imc, font=(FAMILIA, 16, "bold"),
                                  background=CORES["cartao"])
        self.imc_faixa.pack(anchor="w")
        self.imc_dados = ttk.Label(aba_imc, style="CartaoSuave.TLabel")
        self.imc_dados.pack(anchor="w", pady=(4, 20))
        self.regua = tk.Canvas(aba_imc, height=90, background=CORES["cartao"],
                               highlightthickness=0)
        self.regua.pack(fill="x")
        self.regua.bind("<Configure>", lambda _evento: self.desenhar_regua())
        self._imc_atual = None

    # ---------- atualizar ----------
    def atualizar(self):
        self.seletor.definir_itens(self.ctrl.repo.alunos)
        self.atualizar_relatorios()

    def atualizar_relatorios(self):
        aluno = self.seletor.selecionado
        self.seletor_exercicio.definir_itens(self.ctrl.exercicios_com_carga(aluno) if aluno else [])
        self.mostrar_carga()
        self.mostrar_volume()
        self.mostrar_imc()

    def mostrar_carga(self):
        aluno, nome = self.seletor.selecionado, self.seletor_exercicio.selecionado
        if aluno is None or nome is None:
            self.variacao.configure(text="Registre sessões com carga para ver a evolução.")
            self.grafico_carga.mostrar([], [])
            return
        evolucao, variacao = self.ctrl.evolucao_carga(aluno, nome)
        self.variacao.configure(text=f"{nome}: {variacao:+g} kg desde o primeiro treino")
        self.grafico_carga.mostrar([f"{data:%d/%m}" for data, _ in evolucao],
                                   [carga for _, carga in evolucao], "kg")

    def mostrar_volume(self):
        aluno = self.seletor.selecionado
        volumes = self.ctrl.volume_por_semana(aluno) if aluno else {}
        self.grafico_volume.mostrar([semana.replace("Semana ", "Sem. ") for semana in volumes],
                                    list(volumes.values()), "kg")

    def mostrar_imc(self):
        aluno = self.seletor.selecionado
        if aluno is None:
            self._imc_atual = None
            self.imc_numero.configure(text="—", foreground=CORES["texto_suave"])
            self.imc_faixa.configure(text="Nenhum aluno cadastrado", foreground=CORES["texto"])
            self.imc_dados.configure(text="")
        else:
            imc, faixa = self.ctrl.imc(aluno)
            self._imc_atual = imc
            self.imc_numero.configure(text=f"{imc:.2f}", foreground=cor_do_imc(faixa))
            self.imc_faixa.configure(text=faixa, foreground=cor_do_imc(faixa))
            self.imc_dados.configure(text=f"{aluno.nome} · peso {aluno.peso_kg:g} kg · "
                                          f"altura {aluno.altura_m:g} m")
        self.desenhar_regua()

    def desenhar_regua(self):
        """Régua colorida com as faixas de IMC e uma seta no valor do aluno."""
        canvas = self.regua
        canvas.delete("all")
        largura = canvas.winfo_width() - 40
        if largura < 100:
            return
        inicio, fim = FAIXAS_IMC[0][0], FAIXAS_IMC[-1][1]

        def x(valor):
            valor = min(max(valor, inicio), fim)
            return 20 + (valor - inicio) / (fim - inicio) * largura

        for comeco, final, nome in FAIXAS_IMC:
            canvas.create_rectangle(x(comeco), 30, x(final), 52, fill=cor_do_imc(nome),
                                    outline="white", width=2)
            canvas.create_text((x(comeco) + x(final)) / 2, 68, text=nome,
                               fill=CORES["texto_suave"], font=FONTES["pequena"])
            canvas.create_text(x(comeco), 84, text=f"{comeco:g}", fill=CORES["texto_suave"],
                               font=FONTES["pequena"])
        if self._imc_atual is not None:
            px = x(self._imc_atual)
            canvas.create_polygon(px - 8, 6, px + 8, 6, px, 26, fill=CORES["texto"])
