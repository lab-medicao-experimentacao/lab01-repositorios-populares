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
from metrics import extract_rq01_metrics, extract_rq02_metrics


QUERY_PATH = Path(__file__).resolve().parent.parent / "graphql" / "repositories.graphql"
SAMPLE_SIZE = 10 # numero de repo na amostra


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
        print()


def main() -> None:
    try:
        token = get_github_token()
        url = get_github_graphql_url()
        query = load_query(QUERY_PATH)
        data = execute_query(query, {"first": 100}, token, url)
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
            }
        )

    show_sample(repositories, collected_at)


if __name__ == "__main__":
    main()
