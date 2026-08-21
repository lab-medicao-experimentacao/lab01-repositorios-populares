import csv
from datetime import UTC, datetime
from unittest.mock import patch

from project_snapshot import (
    fetch_project_items,
    project_rows,
    write_snapshot,
)


CAPTURED_AT = datetime(2026, 1, 11, 12, 0, tzinfo=UTC)


def _project_page(nodes, has_next_page, end_cursor=None):
    return {
        "organization": {
            "projectV2": {
                "title": "Lab01",
                "url": "https://github.com/orgs/example/projects/1",
                "items": {
                    "nodes": nodes,
                    "pageInfo": {
                        "hasNextPage": has_next_page,
                        "endCursor": end_cursor,
                    },
                },
            }
        }
    }


def _project_item():
    return {
        "content": {
            "number": 10,
            "url": "https://github.com/example/repository/issues/10",
            "title": "Implementar testes",
            "assignees": {"nodes": [{"login": "student"}]},
        },
        "fieldValues": {
            "nodes": [
                {
                    "name": "Doing",
                    "field": {"name": "Status"},
                }
            ]
        },
    }


# Verifica se a próxima página usa o marcador retornado pela página anterior.
def test_fetch_project_items_uses_cursor_across_pages():
    first_item = _project_item()
    second_item = _project_item()
    second_item["content"]["number"] = 11

    with patch("project_snapshot.execute_query") as execute_query:
        execute_query.side_effect = [
            _project_page([first_item], True, "cursor-1"),
            _project_page([second_item], False),
        ]

        project, items = fetch_project_items(
            "query", "owner", 1, "token", "url"
        )

    assert project == {
        "title": "Lab01",
        "url": "https://github.com/orgs/example/projects/1",
    }
    assert [item["content"]["number"] for item in items] == [10, 11]
    assert execute_query.call_args_list[1].args[1]["after"] == "cursor-1"


# Verifica a transformação dos itens do Project em linhas do snapshot.
def test_project_rows_maps_issue_data():
    rows = project_rows(
        {"title": "Lab01", "url": "https://example.com/project"},
        [_project_item()],
        "Lab01S02",
        CAPTURED_AT,
    )

    assert rows == [
        {
            "sprint": "Lab01S02",
            "capturedAt": "2026-01-11",
            "issueNumber": 10,
            "issueUrl": "https://github.com/example/repository/issues/10",
            "issueTitle": "Implementar testes",
            "status": "Doing",
            "assignees": "student",
        }
    ]


# Verifica valores vazios para itens sem conteúdo, status ou responsáveis.
def test_project_rows_handles_item_without_issue_data():
    rows = project_rows(
        {"title": "Lab01", "url": "https://example.com/project"},
        [{}],
        "Lab01S02",
        CAPTURED_AT,
    )

    assert rows[0]["issueNumber"] == ""
    assert rows[0]["status"] == ""
    assert rows[0]["assignees"] == ""


# Verifica o cabeçalho e os valores gravados no arquivo CSV.
def test_write_snapshot_writes_csv(tmp_path):
    rows = project_rows(
        {"title": "Lab01", "url": "https://example.com/project"},
        [_project_item()],
        "Lab01S02",
        CAPTURED_AT,
    )
    output_path = tmp_path / "snapshots" / "kanban_s02.csv"

    write_snapshot(rows, output_path)

    with output_path.open(encoding="utf-8", newline="") as csv_file:
        result = list(csv.DictReader(csv_file))

    assert result == [
        {
            "sprint": "Lab01S02",
            "capturedAt": "2026-01-11",
            "issueNumber": "10",
            "issueUrl": "https://github.com/example/repository/issues/10",
            "issueTitle": "Implementar testes",
            "status": "Doing",
            "assignees": "student",
        }
    ]
