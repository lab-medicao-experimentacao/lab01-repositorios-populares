from unittest.mock import patch

from github_api import fetch_repositories


def _page(nodes, has_next_page, end_cursor=None):
    return {
        "search": {
            "nodes": nodes,
            "pageInfo": {"hasNextPage": has_next_page, "endCursor": end_cursor},
        }
    }


def test_fetch_repositories_single_batch_when_total_fits_in_one_page():
    with patch("github_api.execute_query") as mock_execute:
        mock_execute.return_value = _page(
            [{"nameWithOwner": "a/a"}, {"nameWithOwner": "b/b"}], False
        )

        result = fetch_repositories("query", total=2, batch_size=25, token="t", url="u")

    assert result == [{"nameWithOwner": "a/a"}, {"nameWithOwner": "b/b"}]
    mock_execute.assert_called_once_with("query", {"first": 2, "after": None}, "t", "u")


def test_fetch_repositories_paginates_across_batches_using_cursor():
    with patch("github_api.execute_query") as mock_execute:
        mock_execute.side_effect = [
            _page([{"nameWithOwner": "a/a"}], True, "cursor-1"),
            _page([{"nameWithOwner": "b/b"}], False),
        ]

        result = fetch_repositories("query", total=2, batch_size=1, token="t", url="u")

    assert result == [{"nameWithOwner": "a/a"}, {"nameWithOwner": "b/b"}]
    assert mock_execute.call_args_list[0].args[1] == {"first": 1, "after": None}
    assert mock_execute.call_args_list[1].args[1] == {"first": 1, "after": "cursor-1"}


def test_fetch_repositories_stops_when_no_more_pages_even_if_total_not_reached():
    with patch("github_api.execute_query") as mock_execute:
        mock_execute.return_value = _page([{"nameWithOwner": "a/a"}], False)

        result = fetch_repositories("query", total=5, batch_size=25, token="t", url="u")

    assert result == [{"nameWithOwner": "a/a"}]
    mock_execute.assert_called_once()
