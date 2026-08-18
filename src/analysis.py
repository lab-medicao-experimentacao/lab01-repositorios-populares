import os
from pathlib import Path

import pandas as pd
from scipy import stats

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "output"


def load_dataset() -> pd.DataFrame:
    """Carrega o CSV mais recente do diretório de output."""
    csv_files = sorted(DATA_DIR.glob("repositories_*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"Nenhum CSV encontrado em {DATA_DIR}")
    return pd.read_csv(csv_files[-1])


# ---------- Teste 1: Correlação de Spearman ----------
def test_spearman_age_vs_prs(df: pd.DataFrame) -> None:
    """Correlação de Spearman entre idade (dias) e total de PRs aceitos."""
    cols = ["ageInDays", "mergedPullRequests"]
    subset = df[cols].dropna()

    corr, p_value = stats.spearmanr(subset["ageInDays"], subset["mergedPullRequests"])

    print("=" * 60)
    print("Teste 1 – Correlação de Spearman: ageInDays × mergedPullRequests")
    print("=" * 60)
    print(f"  Coeficiente de correlação (ρ): {corr:.4f}")
    print(f"  p-value:                       {p_value:.6e}")
    print()


if __name__ == "__main__":
    df = load_dataset()
    test_spearman_age_vs_prs(df)
