# LAB01 — Características de repositórios populares

Projeto da disciplina Laboratório de Experimentação de Software para coletar e analisar dados dos repositórios mais populares do GitHub por meio da API GraphQL.

## Sprint atual

Na `Lab01S01`, o grupo coletará os dados necessários para as questões de pesquisa nos 100 repositórios com mais estrelas e validará uma amostra de 5 a 10 repositórios.

## Fonte de referência — linguagens populares (RQ05)

Para a RQ05 ("sistemas populares são escritos nas linguagens mais populares?"), a referência de "linguagens mais populares" usada em todo o laboratório é o [GitHut](https://madnight.github.io/githut/), que baseia o ranking em atividade real de repositórios do GitHub (estrelas, pull requests).

## Estrutura inicial

```text
.
├── data/       # arquivos gerados pela coleta e análise
├── doc/        # enunciado e documentação do trabalho
├── graphql/    # consultas GraphQL
├── src/        # código-fonte Python
└── tests/      # testes automatizados (pytest)
```

## Testes

Instale as dependências de desenvolvimento e rode a suíte:

```bash
pip install -r requirements-dev.txt
pytest
```
