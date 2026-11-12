"""RelatorioEvolucao: calcula a evolução do aluno a partir das sessões."""


class RelatorioEvolucao:
    """DEPENDÊNCIA: o relatório não guarda sessões nem alunos como atributo.

    Ele só recebe esses objetos por parâmetro, usa e devolve o resultado.
    """

    def evolucao_carga(self, sessoes, nome_exercicio):
        """Lista de (data, maior carga do dia) do exercício, em ordem de data."""
        nome = str(nome_exercicio).strip().lower()
        evolucao = []
        for sessao in sorted(sessoes, key=lambda s: s.data):
            cargas = [r.carga_kg for r in sessao.registros
                      if r.exercicio.nome.lower() == nome]
            if cargas:
                evolucao.append((sessao.data, max(cargas)))
        return evolucao

    def variacao_carga(self, sessoes, nome_exercicio):
        """Diferença entre a última e a primeira carga registrada (kg)."""
        evolucao = self.evolucao_carga(sessoes, nome_exercicio)
        if len(evolucao) < 2:
            return 0.0
        return evolucao[-1][1] - evolucao[0][1]

    def volume_por_semana(self, sessoes):
        """Soma o volume das sessões de cada semana do ano."""
        totais = {}
        for sessao in sessoes:
            ano, semana, _ = sessao.data.isocalendar()
            totais[(ano, semana)] = totais.get((ano, semana), 0) + sessao.calcular_volume_total()
        return {f"Semana {semana:02d}/{ano}": totais[(ano, semana)]
                for ano, semana in sorted(totais)}

    def classificar_imc(self, aluno):
        """Devolve o IMC do aluno e a faixa em que ele está."""
        imc = aluno.calcular_imc()
        if imc < 18.5:
            faixa = "Abaixo do peso"
        elif imc < 25:
            faixa = "Peso normal"
        elif imc < 30:
            faixa = "Sobrepeso"
        else:
            faixa = "Obesidade"
        return imc, faixa
