from metrics import extract_rq03_metrics


# Verifica a extração da quantidade de releases.
def test_extract_rq03_metrics_returns_releases_count():
    repository = {"releases": {"totalCount": 15}}

    result = extract_rq03_metrics(repository)

    assert result == {"totalReleases": 15}


# Verifica o resultado para um repositório sem releases.
def test_extract_rq03_metrics_handles_repository_without_releases():
    repository = {"releases": {"totalCount": 0}}

    result = extract_rq03_metrics(repository)

    assert result == {"totalReleases": 0}
