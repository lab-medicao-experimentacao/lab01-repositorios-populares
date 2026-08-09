from datetime import datetime
from typing import Any


def calculate_age_in_days(created_at: str, collected_at: datetime) -> int:
    creation_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    return (collected_at - creation_date).days


def extract_rq01_metrics(
    repository: dict[str, Any],
    collected_at: datetime,
) -> dict[str, Any]:
    return {
        "createdAt": repository["createdAt"],
        "ageInDays": calculate_age_in_days(
            repository["createdAt"],
            collected_at,
        ),
    }


def extract_rq02_metrics(repository: dict[str, Any]) -> dict[str, int]:
    return {
        "mergedPullRequests": repository["pullRequests"]["totalCount"],
    }
