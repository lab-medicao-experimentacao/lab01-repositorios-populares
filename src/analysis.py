"""Análises descritivas e inferenciais sobre repositórios populares do GitHub."""

from pathlib import Path
from typing import Any

import pandas as pd
from scipy import stats

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "output"


def load_dataset() -> pd.DataFrame:
    """Carrega o CSV mais recente do diretório de output."""
    csv_files = sorted(DATA_DIR.glob("repositories_*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"Nenhum CSV encontrado em {DATA_DIR}")
    return pd.read_csv(csv_files[-1])


def validate_rq01(df: pd.DataFrame) -> dict[str, Any]:
    """RQ01 – Validação da coluna ageInDays (idade do repositório)."""
    col = "ageInDays"
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

    print("=" * 60)
    print("Validação RQ01 – Idade do repositório (ageInDays)")
    print("=" * 60)
    print(f"  Total de registros:    {total}")
    print(f"  Valores nulos:         {n_nulls} ({100 * n_nulls / total:.1f}%)")
    print(f"  Mínimo:                {valid.min():.2f}")
    print(f"  Q1 (25%):              {q1:.2f}")
    print(f"  Mediana (50%):         {valid.median():.2f}")
    print(f"  Q3 (75%):              {q3:.2f}")
    print(f"  Máximo:                {valid.max():.2f}")
    print(f"  Média:                 {valid.mean():.2f}")
    print(f"  Desvio padrão:         {valid.std():.2f}")
    print(f"  IQR:                   {iqr:.2f}")
    print(f"  Limites outliers:      [{lower_bound:.2f}, {upper_bound:.2f}]")
    print(f"  Outliers detectados:   {len(outliers)} ({100 * len(outliers) / len(valid):.1f}%)")
    print()

    return {"mediana": valid.median(), "media": valid.mean(), "n_nulls": n_nulls}


def validate_rq02(df: pd.DataFrame) -> dict[str, Any]:
    """RQ02 – Validação da coluna mergedPullRequests (PRs aceitos)."""
    col = "mergedPullRequests"
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

    print("=" * 60)
    print("Validação RQ02 – Total de PRs aceitos (mergedPullRequests)")
    print("=" * 60)
    print(f"  Total de registros:    {total}")
    print(f"  Valores nulos:         {n_nulls} ({100 * n_nulls / total:.1f}%)")
    print(f"  Mínimo:                {valid.min():.2f}")
    print(f"  Q1 (25%):              {q1:.2f}")
    print(f"  Mediana (50%):         {valid.median():.2f}")
    print(f"  Q3 (75%):              {q3:.2f}")
    print(f"  Máximo:                {valid.max():.2f}")
    print(f"  Média:                 {valid.mean():.2f}")
    print(f"  Desvio padrão:         {valid.std():.2f}")
    print(f"  IQR:                   {iqr:.2f}")
    print(f"  Limites outliers:      [{lower_bound:.2f}, {upper_bound:.2f}]")
    print(f"  Outliers detectados:   {len(outliers)} ({100 * len(outliers) / len(valid):.1f}%)")
    print()

    return {"mediana": valid.median(), "media": valid.mean(), "n_nulls": n_nulls}


def validate_rq03(df: pd.DataFrame) -> dict[str, Any]:
    """RQ03 – Validação da coluna totalReleases."""
    col = "totalReleases"
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

    print("=" * 60)
    print("Validação RQ03 – Total de releases (totalReleases)")
    print("=" * 60)
    print(f"  Total de registros:    {total}")
    print(f"  Valores nulos:         {n_nulls} ({100 * n_nulls / total:.1f}%)")
    print(f"  Valores zerados:       {n_zeros} ({100 * n_zeros / len(valid):.1f}%)")
    print(f"  Mínimo:                {valid.min():.2f}")
    print(f"  Q1 (25%):              {q1:.2f}")
    print(f"  Mediana (50%):         {valid.median():.2f}")
    print(f"  Q3 (75%):              {q3:.2f}")
    print(f"  Máximo:                {valid.max():.2f}")
    print(f"  Média:                 {valid.mean():.2f}")
    print(f"  Desvio padrão:         {valid.std():.2f}")
    print(f"  IQR:                   {iqr:.2f}")
    print(f"  Limites outliers:      [{lower_bound:.2f}, {upper_bound:.2f}]")
    print(f"  Outliers detectados:   {len(outliers)} ({100 * len(outliers) / len(valid):.1f}%)")
    print(f"  Obs: {n_zeros} repos sem releases (podem usar rolling release ou ser documentais)")
    print()

    return {"mediana": valid.median(), "media": valid.mean(), "n_nulls": n_nulls, "n_zeros": n_zeros}


def validate_rq04(df: pd.DataFrame) -> dict[str, Any]:
    """RQ04 – Validação da coluna timeSinceLastUpdate."""
    col = "timeSinceLastUpdate"
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

    print("=" * 60)
    print("Validação RQ04 – Tempo desde última atualização (timeSinceLastUpdate)")
    print("=" * 60)
    print(f"  Total de registros:    {total}")
    print(f"  Valores nulos:         {n_nulls} ({100 * n_nulls / total:.1f}%)")
    print(f"  Valores zerados:       {n_zeros} ({100 * n_zeros / len(valid):.1f}%)")
    print(f"  Mínimo:                {valid.min():.2f}")
    print(f"  Q1 (25%):              {q1:.2f}")
    print(f"  Mediana (50%):         {valid.median():.2f}")
    print(f"  Q3 (75%):              {q3:.2f}")
    print(f"  Máximo:                {valid.max():.2f}")
    print(f"  Média:                 {valid.mean():.2f}")
    print(f"  Desvio padrão:         {valid.std():.2f}")
    print(f"  IQR:                   {iqr:.2f}")
    print(f"  Limites outliers:      [{lower_bound:.2f}, {upper_bound:.2f}]")
    print(f"  Outliers detectados:   {len(outliers)} ({100 * len(outliers) / len(valid):.1f}%)")
    print(f"  Obs: {n_zeros} repos com valor 0 (atualizados no dia da coleta).")
    print(f"       Variação insuficiente para categorização binária Ativo/Dormente.")
    print()

    return {"mediana": valid.median(), "media": valid.mean(), "n_nulls": n_nulls, "n_zeros": n_zeros}


def validate_rq05(df: pd.DataFrame) -> dict[str, Any]:
    """RQ05 – Validação da coluna primaryLanguage."""
    total = len(df)
    n_nulls = df["primaryLanguage"].isna().sum()
    n_valid = total - n_nulls
    n_unique = df["primaryLanguage"].nunique()
    lang_counts = df["primaryLanguage"].value_counts()
    top3_langs = lang_counts.head(3).index.tolist()

    print("=" * 60)
    print("Validação RQ05 – Linguagem primária (primaryLanguage)")
    print("=" * 60)
    print(f"  Total de registros:    {total}")
    print(f"  Valores nulos:         {n_nulls} ({100 * n_nulls / total:.1f}%)")
    print(f"  Linguagens distintas:  {n_unique}")
    print(f"  Top 5 linguagens:")
    for lang, count in lang_counts.head(5).items():
        print(f"    {lang:<20} {count:>4} ({100 * count / n_valid:.1f}%)")
    print()

    return {
        "top3_langs": top3_langs,
        "lang_counts": lang_counts,
        "n_valid_lang": n_valid,
    }


def validate_rq06(df: pd.DataFrame) -> dict[str, Any]:
    """RQ06 – Validação de totalIssues, closedIssues e closedIssuesRatio."""
    total = len(df)
    n_nulls_ratio = df["closedIssuesRatio"].isna().sum()
    n_zero_issues = (df["totalIssues"] == 0).sum()

    ratio_when_zero = df.loc[df["totalIssues"] == 0, "closedIssuesRatio"]
    inconsistent = ratio_when_zero.notna().sum()

    valid_ratio = df["closedIssuesRatio"].dropna()
    q1 = valid_ratio.quantile(0.25)
    q3 = valid_ratio.quantile(0.75)
    iqr = q3 - q1
    lower_bound = max(0, q1 - 1.5 * iqr)
    upper_bound = min(1, q3 + 1.5 * iqr)
    outliers = valid_ratio[(valid_ratio < lower_bound) | (valid_ratio > upper_bound)]

    print("=" * 60)
    print("Validação RQ06 – Razão de issues fechadas (closedIssuesRatio)")
    print("=" * 60)
    print(f"  Total de registros:        {total}")
    print(f"  Nulos em closedIssuesRatio:{n_nulls_ratio} ({100 * n_nulls_ratio / total:.1f}%)")
    print(f"  Repos com totalIssues = 0: {n_zero_issues} ({100 * n_zero_issues / total:.1f}%)")
    print(f"  Inconsistências (ratio válida com totalIssues=0): {inconsistent}")
    print(f"  closedIssuesRatio (n={len(valid_ratio)}):")
    print(f"    Mínimo:    {valid_ratio.min():.4f}")
    print(f"    Q1:        {q1:.4f}")
    print(f"    Mediana:   {valid_ratio.median():.4f}")
    print(f"    Q3:        {q3:.4f}")
    print(f"    Máximo:    {valid_ratio.max():.4f}")
    print(f"    Média:     {valid_ratio.mean():.4f}")
    print(f"    IQR:       {iqr:.4f}")
    print(f"    Limites:   [{lower_bound:.4f}, {upper_bound:.4f}]")
    print(f"    Outliers:  {len(outliers)} ({100 * len(outliers) / len(valid_ratio):.1f}%)")
    print()

    return {"mediana_razao_issues": valid_ratio.median()}


def validate_rq07(df: pd.DataFrame, top3_langs: list[str]) -> dict[str, Any]:
    """RQ07 – Prontidão do cruzamento linguagem × mergedPullRequests."""
    cross = df[["primaryLanguage", "mergedPullRequests"]].dropna()
    cross_top3 = cross[cross["primaryLanguage"].isin(top3_langs)]

    print("=" * 60)
    print("Validação RQ07 – Agrupamento linguagem × mergedPullRequests")
    print("=" * 60)
    print(f"  Registros com ambas colunas preenchidas: {len(cross)}")
    print(f"  Top 3 linguagens: {top3_langs}")
    for lang in top3_langs:
        n = len(cross_top3[cross_top3["primaryLanguage"] == lang])
        print(f"    {lang:<20} n={n}")
    print(f"  Total para o teste: {len(cross_top3)} registros")
    print()

    return {"n_cross": len(cross_top3)}


# ==========================================================
# Testes inferenciais
# ==========================================================


def test_spearman(df: pd.DataFrame) -> dict[str, float]:
    """Teste 1 – Correlação de Spearman: ageInDays × mergedPullRequests."""
    subset = df[["ageInDays", "mergedPullRequests"]].dropna()
    corr, p_value = stats.spearmanr(subset["ageInDays"], subset["mergedPullRequests"])

    print("=" * 60)
    print("Teste 1 – Correlação de Spearman: ageInDays × mergedPullRequests")
    print("=" * 60)
    print(f"  Coeficiente de correlação (ρ): {corr:.4f}")
    print(f"  p-value:                       {p_value:.6e}")
    print()

    return {"spearman_rho": corr, "spearman_p_value": p_value}


def test_mann_whitney(df: pd.DataFrame) -> dict[str, float]:
    """Teste 2 – Mann-Whitney U: closedIssuesRatio (Maduro vs Jovem)."""
    subset = df[["ageInDays", "closedIssuesRatio"]].dropna()
    median_age = subset["ageInDays"].median()

    maduros = subset.loc[subset["ageInDays"] > median_age, "closedIssuesRatio"]
    jovens = subset.loc[subset["ageInDays"] <= median_age, "closedIssuesRatio"]

    stat, p_value = stats.mannwhitneyu(maduros, jovens, alternative="two-sided")

    print("=" * 60)
    print("Teste 2 – Mann-Whitney U: closedIssuesRatio (Maduro vs Jovem)")
    print("=" * 60)
    print(f"  Critério: ageInDays > mediana ({median_age:.0f}) → Maduro; <= → Jovem")
    print(f"  n(Maduros) = {len(maduros)}")
    print(f"  n(Jovens)  = {len(jovens)}")
    print(f"  Mediana (Maduros): {maduros.median():.4f}")
    print(f"  Mediana (Jovens):  {jovens.median():.4f}")
    print(f"  U-statistic: {stat:.2f}")
    print(f"  p-value:     {p_value:.6e}")
    print()

    return {
        "mann_whitney_u": stat,
        "mann_whitney_p_value": p_value,
        "mediana_razao_maduros": maduros.median(),
        "mediana_razao_jovens": jovens.median(),
    }


def test_kruskal_wallis(df: pd.DataFrame, top3_langs: list[str]) -> dict[str, Any]:
    """Teste 3 – Kruskal-Wallis H: mergedPullRequests por linguagem (top 3)."""
    subset = df[["primaryLanguage", "mergedPullRequests"]].dropna()
    subset = subset[subset["primaryLanguage"].isin(top3_langs)]

    groups = [
        group["mergedPullRequests"].values
        for _, group in subset.groupby("primaryLanguage")
    ]

    stat, p_value = stats.kruskal(*groups)

    print("=" * 60)
    print("Teste 3 – Kruskal-Wallis H: mergedPullRequests por linguagem")
    print("=" * 60)
    print(f"  Linguagens analisadas: {top3_langs}")
    for lang in top3_langs:
        lang_data = subset.loc[subset["primaryLanguage"] == lang, "mergedPullRequests"]
        print(f"    {lang:>12}: n={len(lang_data)}, mediana={lang_data.median():.1f}")
    print(f"  H-statistic: {stat:.4f}")
    print(f"  p-value:     {p_value:.6e}")
    print()

    return {"kruskal_wallis_h": stat, "kruskal_wallis_p_value": p_value}


# ==========================================================
# Exportação consolidada
# ==========================================================


def export_metrics_csv(
    df: pd.DataFrame,
    rq01: dict[str, Any],
    rq02: dict[str, Any],
    rq03: dict[str, Any],
    rq04: dict[str, Any],
    rq05: dict[str, Any],
    rq06: dict[str, Any],
    spearman: dict[str, float],
    mann_whitney: dict[str, float],
    kruskal: dict[str, Any],
) -> None:
    """Consolida métricas de todas as análises e exporta CSV chave-valor."""
    metrics: dict[str, Any] = {}

    # Medianas descritivas
    metrics["mediana_idade_dias"] = rq01["mediana"]
    metrics["mediana_idade_anos"] = round(rq01["mediana"] / 365, 2)
    metrics["mediana_prs_aceitos"] = rq02["mediana"]
    metrics["mediana_releases"] = rq03["mediana"]
    metrics["mediana_dias_atualizacao"] = rq04["mediana"]

    # Top 3 linguagens
    top3_langs = rq05["top3_langs"]
    lang_counts = rq05["lang_counts"]
    n_valid_lang = rq05["n_valid_lang"]

    for i, lang in enumerate(top3_langs, start=1):
        metrics[f"top{i}_linguagem"] = lang
        metrics[f"top{i}_percentual"] = round(100 * lang_counts[lang] / n_valid_lang, 2)

    # Mediana razão issues fechadas (%)
    metrics["mediana_razao_issues_fechadas_pct"] = round(rq06["mediana_razao_issues"] * 100, 2)

    # Medianas agrupadas por top 3 linguagens
    df_top3 = df[df["primaryLanguage"].isin(top3_langs)]
    for i, lang in enumerate(top3_langs, start=1):
        lang_df = df_top3[df_top3["primaryLanguage"] == lang]
        metrics[f"top{i}_mediana_prs"] = lang_df["mergedPullRequests"].dropna().median()
        metrics[f"top{i}_mediana_releases"] = lang_df["totalReleases"].dropna().median()
        metrics[f"top{i}_mediana_dias_atualizacao"] = lang_df["timeSinceLastUpdate"].dropna().median()

    # Testes estatísticos
    metrics["spearman_rho"] = round(spearman["spearman_rho"], 6)
    metrics["spearman_p_value"] = spearman["spearman_p_value"]

    metrics["mann_whitney_u"] = mann_whitney["mann_whitney_u"]
    metrics["mann_whitney_p_value"] = mann_whitney["mann_whitney_p_value"]
    metrics["mediana_razao_maduros"] = round(mann_whitney["mediana_razao_maduros"], 4)
    metrics["mediana_razao_jovens"] = round(mann_whitney["mediana_razao_jovens"], 4)

    metrics["kruskal_wallis_h"] = round(kruskal["kruskal_wallis_h"], 4)
    metrics["kruskal_wallis_p_value"] = kruskal["kruskal_wallis_p_value"]

    # Exportar
    output_path = DATA_DIR / "metricas_artigo_msr.csv"
    result_df = pd.DataFrame(list(metrics.items()), columns=["Metrica", "Valor"])
    result_df.to_csv(output_path, index=False)

    print("=" * 60)
    print(f"Métricas exportadas → {output_path}")
    print("=" * 60)
    print(result_df.to_string(index=False))
    print()


# ==========================================================
# Execução principal
# ==========================================================


if __name__ == "__main__":
    df = load_dataset()

    # Validações individuais
    rq01 = validate_rq01(df)
    rq02 = validate_rq02(df)
    rq03 = validate_rq03(df)
    rq04 = validate_rq04(df)
    rq05 = validate_rq05(df)
    rq06 = validate_rq06(df)
    rq07 = validate_rq07(df, top3_langs=rq05["top3_langs"])

    # Testes inferenciais
    spearman = test_spearman(df)
    mann_whitney = test_mann_whitney(df)
    kruskal = test_kruskal_wallis(df, top3_langs=rq05["top3_langs"])

    # Exportação consolidada
    export_metrics_csv(df, rq01, rq02, rq03, rq04, rq05, rq06, spearman, mann_whitney, kruskal)
