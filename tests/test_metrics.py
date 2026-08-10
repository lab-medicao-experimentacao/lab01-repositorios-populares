from metrics import extract_rq05_metrics, extract_rq06_metrics


def test_extract_rq05_metrics_returns_language_name():
    repository = {"primaryLanguage": {"name": "Python"}}

    result = extract_rq05_metrics(repository)

    assert result == {"primaryLanguage": "Python"}


def test_extract_rq05_metrics_handles_missing_language():
    repository = {"primaryLanguage": None}

    result = extract_rq05_metrics(repository)

    assert result == {"primaryLanguage": None}


def test_extract_rq06_metrics_calculates_ratio():
    repository = {
        "issues": {"totalCount": 10},
        "closedIssues": {"totalCount": 4},
    }

    result = extract_rq06_metrics(repository)

    assert result == {
        "totalIssues": 10,
        "closedIssues": 4,
        "closedIssuesRatio": 0.4,
    }


def test_extract_rq06_metrics_handles_zero_issues():
    repository = {
        "issues": {"totalCount": 0},
        "closedIssues": {"totalCount": 0},
    }

    result = extract_rq06_metrics(repository)

    assert result == {
        "totalIssues": 0,
        "closedIssues": 0,
        "closedIssuesRatio": None,
    }
