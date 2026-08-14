from metrics import extract_rq02_metrics


# Verifica a extração da quantidade de pull requests aceitas.
def test_extract_rq02_metrics_returns_merged_pull_requests_count():
    repository = {"pullRequests": {"totalCount": 120}}

    result = extract_rq02_metrics(repository)

    assert result == {"mergedPullRequests": 120}


# Verifica o resultado para um repositório sem pull requests aceitas.
def test_extract_rq02_metrics_handles_repository_without_merged_pull_requests():
    repository = {"pullRequests": {"totalCount": 0}}

    result = extract_rq02_metrics(repository)

    assert result == {"mergedPullRequests": 0}
