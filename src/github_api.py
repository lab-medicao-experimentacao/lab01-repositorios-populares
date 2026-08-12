import json
import os
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class GitHubAPIError(RuntimeError):
    """Erro ao preparar ou executar uma consulta na API do GitHub."""


def get_github_token() -> str:
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        raise GitHubAPIError(
            "A variável de ambiente GITHUB_TOKEN não está configurada."
        )

    return token


def get_github_graphql_url() -> str:
    url = os.getenv("GITHUB_GRAPHQL_URL")

    if not url:
        raise GitHubAPIError(
            "A variável de ambiente GITHUB_GRAPHQL_URL não está configurada."
        )

    return url


def load_query(query_path: Path) -> str:
    try:
        return query_path.read_text(encoding="utf-8")
    except OSError as error:
        raise GitHubAPIError(
            f"Não foi possível ler a consulta GraphQL: {query_path}"
        ) from error


def execute_query(query: str, variables: dict[str, Any], token: str, url: str) -> dict[str, Any]:
    payload = json.dumps(
        {
            "query": query, 
            "variables": variables
        }
    ).encode("utf-8")

    request = Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "lab01-repositorios-populares",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=30) as response: # envia a req
            result = json.load(response)
    except HTTPError as error:
        raise GitHubAPIError(
            f"O GitHub respondeu com o status HTTP {error.code}."
        ) from error
    except URLError as error:
        raise GitHubAPIError(
            f"Não foi possível conectar à API do GitHub: {error.reason}"
        ) from error

    if result.get("errors"):
        messages = "; ".join(
            error.get("message", "Erro GraphQL desconhecido")
            for error in result["errors"]
        )
        raise GitHubAPIError(f"A consulta GraphQL falhou: {messages}")

    data = result.get("data")
    if not isinstance(data, dict):
        raise GitHubAPIError("A resposta do GitHub não contém dados válidos.")

    return data


def fetch_repositories(
    query: str,
    total: int,
    batch_size: int,
    token: str,
    url: str,
) -> list[dict[str, Any]]:
    """
    Busca repositorios em lotes de ate batch_size, em vez de uma unica
    chamada com first=total, para evitar erros 502/504 do GitHub ao
    agregar contagens (PRs, releases, issues) para muitos repositorios
    numa unica consulta (ver Issue #13).
    """
    repositories: list[dict[str, Any]] = []
    cursor: str | None = None

    while len(repositories) < total:
        remaining = total - len(repositories)
        data = execute_query(
            query,
            {"first": min(batch_size, remaining), "after": cursor},
            token,
            url,
        )
        search = data["search"]
        repositories.extend(search["nodes"])

        page_info = search["pageInfo"]
        if not page_info["hasNextPage"]:
            break
        cursor = page_info["endCursor"]

    return repositories
