# LAB01 — Características de repositórios populares

[![Tests](https://github.com/lab-medicao-experimentacao/lab01-repositorios-populares/actions/workflows/tests.yml/badge.svg)](https://github.com/lab-medicao-experimentacao/lab01-repositorios-populares/actions/workflows/tests.yml)

Projeto da disciplina Laboratório de Experimentação de Software para coletar e analisar dados dos repositórios mais populares do GitHub por meio da API GraphQL.

## Sprint atual

Na `Lab01S02`, o grupo coleta os 1.000 repositórios mais populares, exporta os
dados em CSV, valida as métricas e registra o estado do board ao final da sprint.

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

## Dashboard (Streamlit)

Com o CSV de repositórios já coletado (`python src/main.py`), visualize as
métricas e gráficos das RQ01 a RQ07 com:

```bash
pip install -r requirements.txt
streamlit run src/dashboard.py
```

## Snapshot do GitHub Projects

Configure `GITHUB_PROJECT_OWNER` e `GITHUB_PROJECT_NUMBER` no `.env`. O token
informado em `GITHUB_TOKEN` precisa de permissão de leitura para Projects v2.

Para gerar o CSV de fechamento da `Lab01S02` sem sobrescrever o snapshot anterior:

```bash
docker compose run --rm \
  -e PROJECT_SNAPSHOT_SPRINT=Lab01S02 \
  -e PROJECT_SNAPSHOT_PATH=data/snapshots/kanban_s02.csv \
  app python src/project_snapshot.py
```

Cada linha registra a sprint, a data da coleta, o número, link e título da Issue,
seu `Status` atual e os responsáveis. Sem as variáveis opcionais acima, o script
mantém a compatibilidade com a S01 e salva em `data/snapshots/kanban_s01.csv`.
