"""Análises descritivas e inferenciais sobre repositórios populares do GitHub."""

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


# ---------- Teste 2: Mann-Whitney U ----------
def test_mann_whitney_maturity(df: pd.DataFrame) -> None:
    """Mann-Whitney U comparando razão de issues fechadas entre repos Maduros e Jovens."""
    subset = df[["ageInDays", "closedIssuesRatio"]].dropna()

    median_age = subset["ageInDays"].median()

    subset = subset.assign(
        maturidade=subset["ageInDays"].apply(
            lambda d: "Maduro" if d > median_age else "Jovem"
        )
    )

    maduros = subset.loc[subset["maturidade"] == "Maduro", "closedIssuesRatio"]
    jovens = subset.loc[subset["maturidade"] == "Jovem", "closedIssuesRatio"]

    stat, p_value = stats.mannwhitneyu(maduros, jovens, alternative="two-sided")

    print("=" * 60)
    print("Teste 2 – Mann-Whitney U: closedIssuesRatio (Maduro vs Jovem)")
    print("=" * 60)
    print(f"  Critério: ageInDays > mediana ({median_age:.0f}) → Maduro; <= mediana → Jovem")
    print(f"  n(Maduros) = {len(maduros)}")
    print(f"  n(Jovens)  = {len(jovens)}")
    print(f"  Mediana (Maduros): {maduros.median():.4f}")
    print(f"  Mediana (Jovens):  {jovens.median():.4f}")
    print(f"  U-statistic: {stat:.2f}")
    print(f"  p-value:     {p_value:.6e}")
    print()


# ---------- Teste 3: Kruskal-Wallis H ----------
def test_kruskal_wallis_languages(df: pd.DataFrame) -> None:
    """Kruskal-Wallis H comparando mergedPullRequests entre as 3 linguagens mais frequentes."""
    subset = df[["primaryLanguage", "mergedPullRequests"]].dropna()

    top3 = subset["primaryLanguage"].value_counts().head(3).index.tolist()
    subset = subset[subset["primaryLanguage"].isin(top3)]

    groups = [
        group["mergedPullRequests"].values
        for _, group in subset.groupby("primaryLanguage")
    ]

    stat, p_value = stats.kruskal(*groups)

    print("=" * 60)
    print("Teste 3 – Kruskal-Wallis H: mergedPullRequests por linguagem")
    print("=" * 60)
    print(f"  Linguagens analisadas: {top3}")
    for lang in top3:
        lang_data = subset.loc[subset["primaryLanguage"] == lang, "mergedPullRequests"]
        print(f"    {lang:>12}: n={len(lang_data)}, mediana={lang_data.median():.1f}")
    print(f"  H-statistic: {stat:.4f}")
    print(f"  p-value:     {p_value:.6e}")
    print()


if __name__ == "__main__":
    df = load_dataset()
    test_spearman_age_vs_prs(df)
    test_mann_whitney_maturity(df)
    test_kruskal_wallis_languages(df)
