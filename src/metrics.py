import statistics
from datetime import datetime
from typing import Any


def _calculate_age_in_days(created_at: str, collected_at: datetime) -> int:
    creation_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    return (collected_at - creation_date).days

def _calculate_time_since_update(
    last_updated: str,
    collected_at: datetime,
) -> int:
    """
    Calculates the time in days since the last update in the repository.
    """
    updated_date = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
    return (collected_at - updated_date).days


def extract_rq01_metrics(
    repository: dict[str, Any],
    collected_at: datetime,
) -> dict[str, Any]:
    return {
        "createdAt": repository["createdAt"],
        "ageInDays": _calculate_age_in_days(
            repository["createdAt"],
            collected_at,
        ),
    }


def extract_rq02_metrics(repository: dict[str, Any]) -> dict[str, int]:
    return {
        "mergedPullRequests": repository["pullRequests"]["totalCount"],
    }

def extract_rq03_metrics(
    repository: dict[str, Any]
) -> dict[str, int]:
    """
    Collects the total number of releases in the selected repositories.
    """
    return {
        "totalReleases": repository["releases"]["totalCount"]
    }

def extract_rq04_metrics(
    repository: dict[str, Any],
    collected_at: datetime
):
    """
    Collects the time in seconds since the last update in a given repo at a given time.
    """
    return {
        "timeSinceLastUpdate": _calculate_time_since_update(
            repository["updatedAt"],
            collected_at
        )
    }


def extract_rq05_metrics(repository: dict[str, Any]) -> dict[str, Any]:
    """
    Collects the primary language of the repository.
    """
    language = repository["primaryLanguage"]
    return {
        "primaryLanguage": language["name"] if language else None,
    }


def extract_rq06_metrics(repository: dict[str, Any]) -> dict[str, Any]:
    """
    Collects the ratio of closed issues to total issues in the repository.
    """
    total_issues = repository["issues"]["totalCount"]
    closed_issues = repository["closedIssues"]["totalCount"]
    return {
        "totalIssues": total_issues,
        "closedIssues": closed_issues,
        "closedIssuesRatio": closed_issues / total_issues if total_issues else None,
    }


def extract_rq07_metrics(
    repositories: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """
    Agrupa PRs aceitas (RQ02), releases (RQ03) e tempo desde a última
    atualização (RQ04) por linguagem primária (RQ05), calculando a média
    e a mediana de cada métrica por linguagem. A mediana é a medida
    preferencial para discussão (menos sensível a outliers), mas a média
    é mantida para referência.
    """
    languages: dict[str, list[dict[str, Any]]] = {}
    for repository in repositories:
        language = repository["primaryLanguage"] or "Sem linguagem"
        languages.setdefault(language, []).append(repository)

    result: dict[str, dict[str, Any]] = {}
    for language, repos in languages.items():
        count = len(repos)
        merged_prs = [r["mergedPullRequests"] for r in repos]
        releases = [r["totalReleases"] for r in repos]
        time_since_update = [r["timeSinceLastUpdate"] for r in repos]
        result[language] = {
            "repositoryCount": count,
            "avgMergedPullRequests": sum(merged_prs) / count,
            "avgTotalReleases": sum(releases) / count,
            "avgTimeSinceLastUpdate": sum(time_since_update) / count,
            "medianMergedPullRequests": statistics.median(merged_prs),
            "medianTotalReleases": statistics.median(releases),
            "medianTimeSinceLastUpdate": statistics.median(time_since_update),
        }
    return result
