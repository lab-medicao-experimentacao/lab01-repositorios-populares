from metrics import (
    extract_rq05_metrics,
    extract_rq06_metrics,
    group_metrics_by_language,
)


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


def test_group_metrics_by_language_groups_multiple_languages():
    repositories = [
        {
            "primaryLanguage": "Python",
            "mergedPullRequests": 10,
            "totalReleases": 2,
            "timeSinceLastUpdate": 5,
        },
        {
            "primaryLanguage": "TypeScript",
            "mergedPullRequests": 20,
            "totalReleases": 4,
            "timeSinceLastUpdate": 1,
        },
    ]

    result = group_metrics_by_language(repositories)

    assert result == {
        "Python": {
            "repositoryCount": 1,
            "avgMergedPullRequests": 10.0,
            "avgTotalReleases": 2.0,
            "avgTimeSinceLastUpdate": 5.0,
        },
        "TypeScript": {
            "repositoryCount": 1,
            "avgMergedPullRequests": 20.0,
            "avgTotalReleases": 4.0,
            "avgTimeSinceLastUpdate": 1.0,
        },
    }


def test_group_metrics_by_language_averages_same_language():
    repositories = [
        {
            "primaryLanguage": "Python",
            "mergedPullRequests": 10,
            "totalReleases": 2,
            "timeSinceLastUpdate": 4,
        },
        {
            "primaryLanguage": "Python",
            "mergedPullRequests": 20,
            "totalReleases": 4,
            "timeSinceLastUpdate": 6,
        },
    ]

    result = group_metrics_by_language(repositories)

    assert result == {
        "Python": {
            "repositoryCount": 2,
            "avgMergedPullRequests": 15.0,
            "avgTotalReleases": 3.0,
            "avgTimeSinceLastUpdate": 5.0,
        },
    }


def test_group_metrics_by_language_handles_missing_language():
    repositories = [
        {
            "primaryLanguage": None,
            "mergedPullRequests": 5,
            "totalReleases": 1,
            "timeSinceLastUpdate": 3,
        },
    ]

    result = group_metrics_by_language(repositories)

    assert result == {
        "Sem linguagem": {
            "repositoryCount": 1,
            "avgMergedPullRequests": 5.0,
            "avgTotalReleases": 1.0,
            "avgTimeSinceLastUpdate": 3.0,
        },
    }


def test_group_metrics_by_language_handles_empty_list():
    result = group_metrics_by_language([])

    assert result == {}
