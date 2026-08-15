from datetime import UTC, datetime

from metrics import extract_rq01_metrics


COLLECTED_AT = datetime(2026, 1, 11, 12, 0, tzinfo=UTC)


# Verifica o cálculo da idade do repositório em dias.
def test_extract_rq01_metrics_calculates_repository_age_in_days():
    repository = {"createdAt": "2020-01-10T12:00:00Z"}

    result = extract_rq01_metrics(repository, COLLECTED_AT)

    assert result == {
        "createdAt": "2020-01-10T12:00:00Z",
        "ageInDays": 2193,
    }


# Verifica que apenas dias completos são considerados na idade.
def test_extract_rq01_metrics_considers_only_complete_days():
    repository = {"createdAt": "2026-01-10T13:00:00Z"}

    result = extract_rq01_metrics(repository, COLLECTED_AT)

    assert result["ageInDays"] == 0
