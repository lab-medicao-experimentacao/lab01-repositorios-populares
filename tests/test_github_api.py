from unittest.mock import call, patch

from github_api import fetch_repositories


def _page(nodes, has_next_page, end_cursor=None):
    return {
        "search": {
            "nodes": nodes,
            "pageInfo": {
                "hasNextPage": has_next_page,
                "endCursor": end_cursor,
            },
        }
    }


# Verifica a coleta quando todos os repositórios estão na primeira página.
def test_fetch_repositories_fetches_single_page():
    with patch("github_api.execute_query") as execute_query:
        execute_query.return_value = _page([{"id": 1}, {"id": 2}], False)

        result = fetch_repositories(
            "query", total=2, batch_size=25, token="token", url="url"
        )

    assert result == [{"id": 1}, {"id": 2}]
    execute_query.assert_called_once_with(
        "query",
        {"first": 2, "after": None},
        "token",
        "url",
    )


# Verifica se a próxima página usa o marcador retornado pela página anterior.
def test_fetch_repositories_uses_cursor_across_pages():
    with patch("github_api.execute_query") as execute_query:
        execute_query.side_effect = [
            _page([{"id": 1}, {"id": 2}], True, "cursor-1"),
            _page([{"id": 3}], False),
        ]

        result = fetch_repositories(
            "query", total=3, batch_size=2, token="token", url="url"
        )

    assert result == [{"id": 1}, {"id": 2}, {"id": 3}]
    assert execute_query.call_args_list == [
        call(
            "query",
            {"first": 2, "after": None},
            "token",
            "url",
        ),
        call(
            "query",
            {"first": 1, "after": "cursor-1"},
            "token",
            "url",
        ),
    ]


# Verifica a interrupção quando a API informa que não existe próxima página.
def test_fetch_repositories_stops_without_next_page():
    with patch("github_api.execute_query") as execute_query:
        execute_query.return_value = _page([{"id": 1}], False)

        result = fetch_repositories(
            "query", total=5, batch_size=2, token="token", url="url"
        )

    assert result == [{"id": 1}]
    execute_query.assert_called_once()


# Verifica que nenhuma requisição é feita quando o total solicitado é zero.
def test_fetch_repositories_handles_zero_total():
    with patch("github_api.execute_query") as execute_query:
        result = fetch_repositories(
            "query", total=0, batch_size=25, token="token", url="url"
        )

    assert result == []
    execute_query.assert_not_called()
