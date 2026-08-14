from datetime import UTC, datetime

from metrics import extract_rq04_metrics


COLLECTED_AT = datetime(2026, 1, 11, 12, 0, tzinfo=UTC)


# Verifica o cálculo dos dias desde a última atualização.
def test_extract_rq04_metrics_calculates_days_since_last_update():
    repository = {"updatedAt": "2026-01-01T12:00:00Z"}

    result = extract_rq04_metrics(repository, COLLECTED_AT)

    assert result == {"timeSinceLastUpdate": 10}


# Verifica que apenas dias completos desde a atualização são considerados.
def test_extract_rq04_metrics_considers_only_complete_days():
    repository = {"updatedAt": "2026-01-10T13:00:00Z"}

    result = extract_rq04_metrics(repository, COLLECTED_AT)

    assert result["timeSinceLastUpdate"] == 0
