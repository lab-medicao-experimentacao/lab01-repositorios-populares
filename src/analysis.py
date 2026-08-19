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


# ---------- Validação de Dados: RQ01 e RQ02 ----------
def validate_rq01_rq02(df: pd.DataFrame) -> None:
    """Análise de consistência das colunas ageInDays e mergedPullRequests."""
    columns = {"ageInDays": "RQ01 – Idade do repositório (dias)",
               "mergedPullRequests": "RQ02 – Total de PRs aceitos"}

    print("=" * 60)
    print("Validação de Dados – RQ01 e RQ02")
    print("=" * 60)

    for col, label in columns.items():
        series = df[col]
        total = len(series)
        n_nulls = series.isna().sum()
        valid = series.dropna()

        q1 = valid.quantile(0.25)
        q3 = valid.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = valid[(valid < lower_bound) | (valid > upper_bound)]

        print(f"\n  {label} ({col})")
        print(f"  {'-' * 50}")
        print(f"    Total de registros:    {total}")
        print(f"    Valores nulos:         {n_nulls} ({100 * n_nulls / total:.1f}%)")
        print(f"    Mínimo:                {valid.min():.2f}")
        print(f"    Q1 (25%):              {q1:.2f}")
        print(f"    Mediana (50%):         {valid.median():.2f}")
        print(f"    Q3 (75%):              {q3:.2f}")
        print(f"    Máximo:                {valid.max():.2f}")
        print(f"    Média:                 {valid.mean():.2f}")
        print(f"    Desvio padrão:         {valid.std():.2f}")
        print(f"    IQR:                   {iqr:.2f}")
        print(f"    Limites outliers:      [{lower_bound:.2f}, {upper_bound:.2f}]")
        print(f"    Outliers detectados:   {len(outliers)} ({100 * len(outliers) / len(valid):.1f}%)")

    print()


# ---------- Validação de Dados: RQ03 e RQ04 ----------
def validate_rq03_rq04(df: pd.DataFrame) -> None:
    """Análise de consistência das colunas totalReleases e timeSinceLastUpdate."""
    columns = {"totalReleases": "RQ03 – Total de releases",
               "timeSinceLastUpdate": "RQ04 – Tempo desde última atualização (dias)"}

    print("=" * 60)
    print("Validação de Dados – RQ03 e RQ04")
    print("=" * 60)

    for col, label in columns.items():
        series = df[col]
        total = len(series)
        n_nulls = series.isna().sum()
        valid = series.dropna()

        n_zeros = (valid == 0).sum()

        q1 = valid.quantile(0.25)
        q3 = valid.quantile(0.75)
        iqr = q3 - q1
        lower_bound = max(0, q1 - 1.5 * iqr)
        upper_bound = q3 + 1.5 * iqr
        outliers = valid[(valid < lower_bound) | (valid > upper_bound)]

        print(f"\n  {label} ({col})")
        print(f"  {'-' * 50}")
        print(f"    Total de registros:    {total}")
        print(f"    Valores nulos:         {n_nulls} ({100 * n_nulls / total:.1f}%)")
        print(f"    Valores zerados:       {n_zeros} ({100 * n_zeros / len(valid):.1f}%)")
        print(f"    Mínimo:                {valid.min():.2f}")
        print(f"    Q1 (25%):              {q1:.2f}")
        print(f"    Mediana (50%):         {valid.median():.2f}")
        print(f"    Q3 (75%):              {q3:.2f}")
        print(f"    Máximo:                {valid.max():.2f}")
        print(f"    Média:                 {valid.mean():.2f}")
        print(f"    Desvio padrão:         {valid.std():.2f}")
        print(f"    IQR:                   {iqr:.2f}")
        print(f"    Limites outliers:      [{lower_bound:.2f}, {upper_bound:.2f}]")
        print(f"    Outliers detectados:   {len(outliers)} ({100 * len(outliers) / len(valid):.1f}%)")

    # Inconsistências documentadas
    no_releases = df[df["totalReleases"] == 0]
    print(f"\n  Observações:")
    print(f"    - {len(no_releases)} repositórios ({100 * len(no_releases) / len(df):.1f}%) "
          f"não possuem nenhuma release registrada.")
    print(f"      Isso pode indicar projetos que usam outro modelo de distribuição")
    print(f"      (ex: rolling release, deploy contínuo) ou projetos puramente documentais.")

    all_zero_update = (df["timeSinceLastUpdate"] == 0).sum()
    print(f"    - {all_zero_update} repositórios ({100 * all_zero_update / len(df):.1f}%) "
          f"possuem timeSinceLastUpdate = 0,")
    print(f"      indicando atualização no mesmo dia da coleta. Coluna possui variação")
    print(f"      insuficiente para categorização binária (Ativo/Dormente).")
    print()


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
    validate_rq01_rq02(df)
    validate_rq03_rq04(df)
    test_spearman_age_vs_prs(df)
    test_mann_whitney_maturity(df)
    test_kruskal_wallis_languages(df)
