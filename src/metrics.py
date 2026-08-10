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
