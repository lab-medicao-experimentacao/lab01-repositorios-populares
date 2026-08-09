from pathlib import Path

from github_api import (
    GitHubAPIError,
    execute_query,
    get_github_graphql_url,
    get_github_token,
    load_query,
)


QUERY_PATH = Path(__file__).resolve().parent.parent / "graphql" / "repositories.graphql"


def main() -> None:
    try:
        token = get_github_token()
        url = get_github_graphql_url()
        query = load_query(QUERY_PATH)
        data = execute_query(query, {"first": 100}, token, url)
    except GitHubAPIError as error:
        raise SystemExit(f"Erro: {error}") from error

    repositories = data["search"]["nodes"]


if __name__ == "__main__":
    main()
