# Gerenciador de Treinos

Aplicativo desktop em Python para gerenciar treinos de academia, feito para a disciplina de
Orientação a Objetos (UnB). Permite cadastrar alunos e instrutores, montar fichas de treino
(A, B, C…), registrar os treinos feitos e acompanhar a evolução de carga.

## Como rodar

Requisito: Python 3.10 ou mais novo.

```bash
pip install -r requirements.txt

# menu do terminal
python src/main.py

# testes
python -m pytest -v
```

## Menu do terminal (nível 2)

```
1 - Alunos                      cadastrar, listar, editar e excluir
2 - Instrutores                 cadastrar, listar, vincular/desvincular alunos e excluir
3 - Fichas de treino            criar, listar e excluir fichas de um aluno
4 - Exercícios de uma ficha     adicionar (musculação, cardio ou isométrico), remover e ver
5 - Ver ficha                   descrição e volume de cada exercício e volume total
6 - Registrar sessão de treino  data, duração, observação e o que foi feito em cada exercício
7 - Histórico de sessões        todas as sessões do aluno em ordem de data
8 - Relatórios                  evolução de carga, volume por semana e IMC
9 - Carregar dados de exemplo   instrutor, alunos, fichas e sessões prontos para demonstrar
0 - Sair
```

Todas as entradas são validadas (campo vazio, número negativo, texto no lugar de número,
CPF inválido ou repetido, data inválida, opção inexistente): o programa mostra uma mensagem
de erro e pergunta de novo, em vez de quebrar. Neste nível os dados ficam só na memória
(`RepositorioMemoria`) e somem ao fechar o programa; o banco de dados entra no nível 3.

## Modelagem (nível 1)

![Diagrama de classes](docs/uml.png)

| Relação | Onde aparece |
| --- | --- |
| Herança | `Aluno` e `Instrutor` herdam de `Pessoa`; `ExercicioMusculacao`, `ExercicioCardio` e `ExercicioIsometrico` herdam de `Exercicio` |
| Polimorfismo | `apresentar()` em cada pessoa; `calcular_volume()`, `descricao()` e `descrever_registro()` em cada exercício |
| Composição | `FichaTreino` cria e contém seus `Exercicio`s; `SessaoTreino` cria e contém seus `RegistroExercicio`s |
| Associação | `Instrutor` acompanha `Aluno`s; `Aluno` tem `FichaTreino`s e `SessaoTreino`s; `SessaoTreino` aponta para a ficha feita; `RegistroExercicio` aponta para o exercício |
| Dependência | `RelatorioEvolucao` usa sessões e alunos recebidos por parâmetro, sem guardá-los |

O código-fonte do diagrama está em `docs/uml.puml` (PlantUML).

## Estrutura

```
src/
├── main.py                       # ponto de entrada: abre o menu
├── models/
│   ├── validacao.py              # validação das entradas
│   ├── pessoa.py                 # Pessoa, Aluno, Instrutor
│   ├── exercicio.py              # Exercicio e as 3 subclasses
│   ├── ficha_treino.py           # FichaTreino
│   └── sessao_treino.py          # SessaoTreino, RegistroExercicio
├── services/
│   └── relatorio.py              # RelatorioEvolucao
├── repository/
│   └── repositorio_memoria.py    # guarda alunos e instrutores na memória (nível 2)
└── ui/
    ├── menu_terminal.py          # menu do terminal
    └── dados_exemplo.py          # dados prontos para demonstração
tests/                            # testes com pytest (modelos, repositório e menu)
docs/                             # diagrama UML
```
