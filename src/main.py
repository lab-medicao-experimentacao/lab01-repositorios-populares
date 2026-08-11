from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from github_api import (
    GitHubAPIError,
    execute_query,
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
    group_metrics_by_language,
)


QUERY_PATH = Path(__file__).resolve().parent.parent / "graphql" / "repositories.graphql"
SAMPLE_SIZE = 100# numero de repo na amostra


def show_sample( # amostra
    repositories: list[dict[str, Any]],
    collected_at: datetime,
    sample_size: int = SAMPLE_SIZE, 
) -> None:
    print(f"Data da coleta (UTC): {collected_at.isoformat()}")
    print(f"Amostra para validação: {min(sample_size, len(repositories))} repositórios\n")

    for repository in repositories[:sample_size]:
        print(f"Repositório: {repository['nameWithOwner']}")
        print(f"Estrelas: {repository['stargazerCount']}")
        print(f"Criado em: {repository['createdAt']}")
        print(f"Idade em dias (RQ01): {repository['ageInDays']}")
        print(f"Pull requests aceitas (RQ02): {repository['mergedPullRequests']}")
        print(f"Total de releases (RQ03): {repository['totalReleases']}")
        print(f"Tempo desde o último update (RQ04): {repository['timeSinceLastUpdate']} dias")
        print(f"Linguagem primária (RQ05): {repository['primaryLanguage']}")
        print(f"Issues fechadas/total (RQ06): {repository['closedIssues']}/{repository['totalIssues']} ({repository['closedIssuesRatio']})")
        print("\n")


def show_language_summary(grouped: dict[str, dict[str, Any]]) -> None:
    print("Métricas por linguagem (RQ07)\n")

    for language, metrics in grouped.items():
        print(f"Linguagem: {language} ({metrics['repositoryCount']} repositórios)")
        print(f"  Média de PRs aceitas: {metrics['avgMergedPullRequests']}")
        print(f"  Média de releases: {metrics['avgTotalReleases']}")
        print(
            "  Média de dias desde a última atualização: "
            f"{metrics['avgTimeSinceLastUpdate']}"
        )
        print()


def main() -> None:
    try:
        token = get_github_token()
        url = get_github_graphql_url()
        query = load_query(QUERY_PATH)
        data = execute_query(query, {"first": SAMPLE_SIZE}, token, url)
    except GitHubAPIError as error:
        raise SystemExit(f"Erro: {error}") from error

    collected_at = datetime.now(UTC)
    repositories = []
    for repository in data["search"]["nodes"]:
        repositories.append(
            {
                "nameWithOwner": repository["nameWithOwner"],
                "stargazerCount": repository["stargazerCount"],
                **extract_rq01_metrics(repository, collected_at),
                **extract_rq02_metrics(repository),
                **extract_rq03_metrics(repository),
                **extract_rq04_metrics(repository, collected_at),
                **extract_rq05_metrics(repository),
                **extract_rq06_metrics(repository),
            }
        )

    show_sample(repositories, collected_at)
    show_language_summary(group_metrics_by_language(repositories))


if __name__ == "__main__":
    main()
