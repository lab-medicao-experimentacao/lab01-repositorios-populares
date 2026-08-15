from metrics import extract_rq05_metrics


# Verifica a extração do nome da linguagem primária.
def test_extract_rq05_metrics_returns_primary_language_name():
    repository = {"primaryLanguage": {"name": "Python"}}

    result = extract_rq05_metrics(repository)

    assert result == {"primaryLanguage": "Python"}


# Verifica o resultado quando não há linguagem primária.
def test_extract_rq05_metrics_handles_missing_primary_language():
    repository = {"primaryLanguage": None}

    result = extract_rq05_metrics(repository)

    assert result == {"primaryLanguage": None}
