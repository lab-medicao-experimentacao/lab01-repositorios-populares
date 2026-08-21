import csv
import os
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


ROOT_PATH = Path(__file__).resolve().parent.parent
QUERY_PATH = ROOT_PATH / "graphql" / "project_snapshot.graphql"
PAGE_SIZE = 100


def get_project_config() -> tuple[str, int, Path, str]:
    owner = os.getenv("GITHUB_PROJECT_OWNER")
    project_number = os.getenv("GITHUB_PROJECT_NUMBER")
    output_path = Path(os.getenv("PROJECT_SNAPSHOT_PATH"))
    sprint = os.getenv("PROJECT_SNAPSHOT_SPRINT").strip()

    if not owner:
        raise GitHubAPIError(
            "A variável de ambiente GITHUB_PROJECT_OWNER não está configurada."
        )

    try:
        number = int(project_number or "")
    except ValueError as error:
        raise GitHubAPIError(
            "GITHUB_PROJECT_NUMBER deve conter um número inteiro."
        ) from error

    if number <= 0:
        raise GitHubAPIError("GITHUB_PROJECT_NUMBER deve ser maior que zero.")

    if not sprint:
        raise GitHubAPIError(
            "PROJECT_SNAPSHOT_SPRINT não pode ser uma string vazia."
        )

    return owner, number, output_path, sprint


def fetch_project_items(
    query: str,
    owner: str,
    project_number: int,
    token: str,
    url: str,
) -> tuple[dict[str, str], list[dict[str, Any]]]:
    items: list[dict[str, Any]] = []
    cursor: str | None = None
    project_info: dict[str, str] | None = None

    while True:
        data = execute_query(
            query,
            {
                "owner": owner,
                "projectNumber": project_number,
                "first": PAGE_SIZE,
                "after": cursor,
            },
            token,
            url,
        )
        organization = data.get("organization")
        project = (
            organization.get("projectV2")
            if isinstance(organization, dict)
            else None
        )
        if not isinstance(project, dict):
            raise GitHubAPIError(
                f"Project v2 número {project_number} não encontrado para {owner}."
            )

        if project_info is None:
            project_info = {"title": project["title"], "url": project["url"]}

        project_items = project["items"]
        items.extend(project_items["nodes"])
        page_info = project_items["pageInfo"]
        if not page_info["hasNextPage"]:
            break

        next_cursor = page_info["endCursor"]
        if not next_cursor or next_cursor == cursor:
            raise GitHubAPIError("A paginação do Project não avançou.")
        cursor = next_cursor

    return project_info, items


def _status_from(item: dict[str, Any]) -> str:
    for field_value in item.get("fieldValues", {}).get("nodes", []):
        if field_value.get("field", {}).get("name") == "Status":
            return field_value.get("name") or ""
    return ""


def project_rows(
    project: dict[str, str],
    items: list[dict[str, Any]],
    sprint: str,
    captured_at: datetime,
) -> list[dict[str, Any]]:
    rows = []
    for item in items:
        content = item.get("content") or {}
        assignees = content.get("assignees", {}).get("nodes", [])
        rows.append(
            {
                "sprint": sprint,
                "capturedAt": captured_at.date().isoformat(),
                "issueNumber": content.get("number", ""),
                "issueUrl": content.get("url", ""),
                "issueTitle": content.get("title", ""),
                "status": _status_from(item),
                "assignees": ";".join(assignee["login"] for assignee in assignees),
            }
        )
    return rows


def write_snapshot(rows: list[dict[str, Any]], output_path: Path) -> None:
    fieldnames = [
        "sprint",
        "capturedAt",
        "issueNumber",
        "issueUrl",
        "issueTitle",
        "status",
        "assignees",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    try:
        owner, project_number, output_path, sprint = get_project_config()
        query = load_query(QUERY_PATH)
        project, items = fetch_project_items(
            query,
            owner,
            project_number,
            get_github_token(),
            get_github_graphql_url(),
        )
        rows = project_rows(project, items, sprint, datetime.now(UTC))
        write_snapshot(rows, output_path)
    except GitHubAPIError as error:
        raise SystemExit(f"Erro: {error}") from error

    print(f"Snapshot exportado: {output_path} ({len(rows)} itens)")


if __name__ == "__main__":
    main()
