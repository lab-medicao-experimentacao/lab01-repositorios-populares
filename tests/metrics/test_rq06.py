from metrics import extract_rq06_metrics


# Verifica o cálculo da proporção de issues fechadas.
def test_extract_rq06_metrics_calculates_closed_issues_ratio():
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


# Verifica o resultado para um repositório sem issues.
def test_extract_rq06_metrics_handles_repository_without_issues():
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


# Verifica a proporção máxima quando todas as issues estão fechadas.
def test_extract_rq06_metrics_returns_one_when_all_issues_are_closed():
    repository = {
        "issues": {"totalCount": 8},
        "closedIssues": {"totalCount": 8},
    }

    result = extract_rq06_metrics(repository)

    assert result["closedIssuesRatio"] == 1
