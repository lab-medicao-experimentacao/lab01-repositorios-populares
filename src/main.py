import csv
import logging
from datetime import UTC, datetime
from pathlib import Path

logger = logging.getLogger(__name__)

from github_api import (
    GitHubAPIError,
    fetch_repositories,
    get_github_graphql_url,
    get_github_token,
    load_query,
)
from metrics import (
    extract_rq01_metrics,
    extract_rq02_metrics,
    extract_rq03_metrics,
    extract_rq04_metrics,
    extract_rq05_metrics,
    extract_rq06_metrics,
    extract_rq07_metrics,
)
from models import RepositoryRecord


QUERY_PATH = Path(__file__).resolve().parent.parent / "graphql" / "repositories.graphql"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "output"
SAMPLE_SIZE = 1000  # numero de repositorios consultados na API e exibidos na amostra
BATCH_SIZE = 10  # tamanho de cada lote da consulta, evita 502/504 do GitHub (ver Issue #13)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)


def show_sample(
    repositories: list[RepositoryRecord],
    collected_at: datetime,
    sample_size: int = SAMPLE_SIZE,
) -> None:
    print(f"Data da coleta (UTC): {collected_at.isoformat()}")
    print(f"Amostra para validação: {min(sample_size, len(repositories))} repositórios\n")

    for repository in repositories[:sample_size]:
        print(f"Repositório: {repository.nameWithOwner}")
        print(f"Estrelas: {repository.stargazerCount}")
        print(f"Criado em: {repository.createdAt}")
        print(f"Idade em dias (RQ01): {repository.ageInDays}")
        print(f"Pull requests aceitas (RQ02): {repository.mergedPullRequests}")
        print(f"Total de releases (RQ03): {repository.totalReleases}")
        print(f"Tempo desde o último update (RQ04): {repository.timeSinceLastUpdate} dias")
        print(f"Linguagem primária (RQ05): {repository.primaryLanguage}")
        print(f"Issues fechadas/total (RQ06): {repository.closedIssues}/{repository.totalIssues} ({repository.closedIssuesRatio})")
        print("\n")

    print("Métricas por linguagem (RQ07)\n")
    for language, metrics in extract_rq07_metrics([r.model_dump() for r in repositories]).items():
        print(f"Linguagem: {language} ({metrics['repositoryCount']} repositórios)")
        print(f"  Média de PRs aceitas: {metrics['avgMergedPullRequests']:.2f}")
        print(f"  Mediana de PRs aceitas: {metrics['medianMergedPullRequests']:.2f}")
        print(f"  Média de releases: {metrics['avgTotalReleases']:.2f}")
        print(f"  Mediana de releases: {metrics['medianTotalReleases']:.2f}")
        print(
            "  Média de dias desde a última atualização: "
            f"{metrics['avgTimeSinceLastUpdate']:.2f}"
        )
        print(
            "  Mediana de dias desde a última atualização: "
            f"{metrics['medianTimeSinceLastUpdate']:.2f}"
        )
        print()


def export_to_csv(records: list[RepositoryRecord], collected_at: datetime) -> None:
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    filename = OUTPUT_PATH / f"repositories_{collected_at.strftime('%Y%m%d_%H%M%S')}.csv"
    fields = list(RepositoryRecord.model_fields.keys())

    with filename.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for record in records:
            writer.writerow(record.model_dump())

    logger.info("Resultados exportados para %s", filename)


def main() -> None:
    try:
        token = get_github_token()
        url = get_github_graphql_url()
        query = load_query(QUERY_PATH)
        repositories_data = fetch_repositories(query, SAMPLE_SIZE, BATCH_SIZE, token, url)
    except GitHubAPIError as error:
        logger.error("Erro: %s", error)
        raise SystemExit(1) from error

    collected_at = datetime.now(UTC)
    repositories = []
    for repository in repositories_data:
        repositories.append(
            RepositoryRecord(
                nameWithOwner=repository["nameWithOwner"],
                stargazerCount=repository["stargazerCount"],
                **extract_rq01_metrics(repository, collected_at),
                **extract_rq02_metrics(repository),
                **extract_rq03_metrics(repository),
                **extract_rq04_metrics(repository, collected_at),
                **extract_rq05_metrics(repository),
                **extract_rq06_metrics(repository),
            )
        )

    show_sample(repositories, collected_at, SAMPLE_SIZE)
    export_to_csv(repositories, collected_at)


if __name__ == "__main__":
    main()
