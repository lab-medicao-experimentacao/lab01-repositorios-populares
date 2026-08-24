from metrics import extract_rq07_metrics


def _repository(language, merged_pull_requests, releases, days_since_update):
    return {
        "primaryLanguage": language,
        "mergedPullRequests": merged_pull_requests,
        "totalReleases": releases,
        "timeSinceLastUpdate": days_since_update,
    }


# Verifica o agrupamento das métricas por linguagem.
def test_extract_rq07_metrics_groups_results_by_language():
    repositories = [
        _repository("Python", 10, 2, 4),
        _repository("TypeScript", 20, 4, 1),
    ]

    result = extract_rq07_metrics(repositories)

    assert result == {
        "Python": {
            "repositoryCount": 1,
            "avgMergedPullRequests": 10.0,
            "avgTotalReleases": 2.0,
            "avgTimeSinceLastUpdate": 4.0,
            "medianMergedPullRequests": 10.0,
            "medianTotalReleases": 2.0,
            "medianTimeSinceLastUpdate": 4.0,
        },
        "TypeScript": {
            "repositoryCount": 1,
            "avgMergedPullRequests": 20.0,
            "avgTotalReleases": 4.0,
            "avgTimeSinceLastUpdate": 1.0,
            "medianMergedPullRequests": 20.0,
            "medianTotalReleases": 4.0,
            "medianTimeSinceLastUpdate": 1.0,
        },
    }


# Verifica o cálculo das médias para repositórios da mesma linguagem.
def test_extract_rq07_metrics_calculates_averages_for_same_language():
    repositories = [
        _repository("Python", 10, 2, 4),
        _repository("Python", 20, 4, 6),
    ]

    result = extract_rq07_metrics(repositories)

    assert result == {
        "Python": {
            "repositoryCount": 2,
            "avgMergedPullRequests": 15.0,
            "avgTotalReleases": 3.0,
            "avgTimeSinceLastUpdate": 5.0,
            "medianMergedPullRequests": 15.0,
            "medianTotalReleases": 3.0,
            "medianTimeSinceLastUpdate": 5.0,
        }
    }


# Verifica que mediana e média divergem quando há um outlier (número ímpar de repositórios).
def test_extract_rq07_metrics_median_differs_from_average_with_outlier():
    repositories = [
        _repository("Python", 10, 2, 4),
        _repository("Python", 20, 4, 6),
        _repository("Python", 300, 4, 6),
    ]

    result = extract_rq07_metrics(repositories)

    assert result["Python"]["avgMergedPullRequests"] == 110.0
    assert result["Python"]["medianMergedPullRequests"] == 20.0


# Verifica o agrupamento de repositórios sem linguagem definida.
def test_extract_rq07_metrics_groups_repositories_without_language():
    repositories = [_repository(None, 5, 1, 3)]

    result = extract_rq07_metrics(repositories)

    assert result == {
        "Sem linguagem": {
            "repositoryCount": 1,
            "avgMergedPullRequests": 5.0,
            "avgTotalReleases": 1.0,
            "avgTimeSinceLastUpdate": 3.0,
            "medianMergedPullRequests": 5.0,
            "medianTotalReleases": 1.0,
            "medianTimeSinceLastUpdate": 3.0,
        }
    }


# Verifica o resultado quando a lista de repositórios está vazia.
def test_extract_rq07_metrics_handles_empty_repository_list():
    result = extract_rq07_metrics([])

    assert result == {}
