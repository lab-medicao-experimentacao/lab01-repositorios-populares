"""Geração de gráficos extras para o relatório final.

Cada execução gera 6 PNGs em ``data/output/figures/`` com um timestamp comum
no formato ``YYYYMMDD_HHMMSS_<nome>.png``.

Gráficos gerados:
    1. Heatmap de correlações de Spearman entre as métricas principais
    2. Q-Q plot de mergedPullRequests contra a distribuição normal
    3. Ridge plot de mergedPullRequests por top 5 linguagens
    4. Timeline de createdAt (nascimento dos repositórios populares)
    5. Scatter idade x PRs com linha de tendência (visualização do Spearman)
    6. Boxplot + ECDFs de Maduros vs Jovens (visualização do Mann-Whitney)
"""

from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

from analysis import load_dataset

FIGURES_DIR = Path(__file__).resolve().parent.parent / "data" / "output" / "figures"

# Paleta consistente com o dashboard Streamlit
ACCENT = "#e3b341"
GRID = "#232b33"
TEXT = "#e6edf3"

sns.set_theme(style="whitegrid", context="talk")


def _build_path(timestamp: str, name: str) -> Path:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    return FIGURES_DIR / f"{timestamp}_{name}.png"


def _save(fig: plt.Figure, path: Path) -> None:
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  → {path.relative_to(FIGURES_DIR.parent.parent.parent)}")


# ---------------------------------------------------------------------------
# 1. Heatmap de correlações de Spearman
# ---------------------------------------------------------------------------
def plot_correlation_heatmap(df: pd.DataFrame, timestamp: str) -> None:
    """Heatmap de correlações de Spearman entre métricas numéricas principais."""
    cols = [
        "ageInDays",
        "stargazerCount",
        "mergedPullRequests",
        "totalReleases",
        "closedIssuesRatio",
    ]
    labels = {
        "ageInDays": "Idade (dias)",
        "stargazerCount": "Estrelas",
        "mergedPullRequests": "PRs aceitos",
        "totalReleases": "Releases",
        "closedIssuesRatio": "Razão issues fechadas",
    }
    subset = df[cols].dropna()
    corr = subset.corr(method="spearman")
    corr = corr.rename(index=labels, columns=labels)

    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="RdBu_r",
        center=0,
        vmin=-1,
        vmax=1,
        square=True,
        linewidths=0.5,
        cbar_kws={"label": "Coeficiente de Spearman (ρ)"},
        ax=ax,
    )
    ax.set_title(
        "Correlação de Spearman entre métricas dos repositórios",
        fontsize=14,
        pad=14,
    )
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    plt.setp(ax.get_yticklabels(), rotation=0)
    fig.tight_layout()

    _save(fig, _build_path(timestamp, "correlation_heatmap"))


# ---------------------------------------------------------------------------
# 2. Q-Q plot de mergedPullRequests
# ---------------------------------------------------------------------------
def plot_qq_prs(df: pd.DataFrame, timestamp: str) -> None:
    """Q-Q plot de mergedPullRequests vs. distribuição normal."""
    values = df["mergedPullRequests"].dropna().values

    fig, axes = plt.subplots(1, 2, figsize=(13, 6))

    # (a) Escala linear — evidencia a assimetria extrema
    stats.probplot(values, dist="norm", plot=axes[0])
    axes[0].set_title("Q-Q plot — escala linear", fontsize=13, pad=10)
    axes[0].set_xlabel("Quantis teóricos (Normal)")
    axes[0].set_ylabel("Quantis amostrais — PRs aceitos")
    axes[0].get_lines()[0].set_markerfacecolor(ACCENT)
    axes[0].get_lines()[0].set_markeredgecolor(ACCENT)
    axes[0].get_lines()[0].set_markersize(5)
    axes[0].get_lines()[1].set_color("#c9302c")

    # (b) log1p — mesmo assim a distribuição não é normal
    log_values = np.log1p(values)
    stats.probplot(log_values, dist="norm", plot=axes[1])
    axes[1].set_title("Q-Q plot — após log(1 + x)", fontsize=13, pad=10)
    axes[1].set_xlabel("Quantis teóricos (Normal)")
    axes[1].set_ylabel("Quantis amostrais — log(1 + PRs)")
    axes[1].get_lines()[0].set_markerfacecolor(ACCENT)
    axes[1].get_lines()[0].set_markeredgecolor(ACCENT)
    axes[1].get_lines()[0].set_markersize(5)
    axes[1].get_lines()[1].set_color("#c9302c")

    fig.suptitle(
        "Q-Q plot de PRs aceitos: desvio da normalidade justifica testes não-paramétricos",
        fontsize=14,
        y=1.02,
    )
    fig.tight_layout()

    _save(fig, _build_path(timestamp, "qq_plot_prs"))


# ---------------------------------------------------------------------------
# 3. Ridge plot de mergedPullRequests por top 5 linguagens
# ---------------------------------------------------------------------------
def plot_ridge_prs_by_language(df: pd.DataFrame, timestamp: str, top_n: int = 5) -> None:
    """Ridge (joy) plot da distribuição de PRs para as top N linguagens."""
    subset = df[["primaryLanguage", "mergedPullRequests"]].dropna()
    top_langs = subset["primaryLanguage"].value_counts().head(top_n).index.tolist()
    subset = subset[subset["primaryLanguage"].isin(top_langs)].copy()
    subset["log_prs"] = np.log1p(subset["mergedPullRequests"])

    # Ordenar linguagens pela mediana descendente (mais engajadas no topo)
    order = (
        subset.groupby("primaryLanguage")["mergedPullRequests"]
        .median()
        .sort_values(ascending=False)
        .index.tolist()
    )

    palette = sns.color_palette("magma", n_colors=len(order))

    grid = sns.FacetGrid(
        subset,
        row="primaryLanguage",
        row_order=order,
        hue="primaryLanguage",
        hue_order=order,
        palette=palette,
        aspect=6,
        height=1.4,
        sharey=False,
    )

    grid.map(
        sns.kdeplot,
        "log_prs",
        clip_on=False,
        fill=True,
        alpha=0.65,
        linewidth=1.5,
        bw_adjust=0.9,
    )
    grid.map(sns.kdeplot, "log_prs", clip_on=False, color="black", lw=1.2, bw_adjust=0.9)

    def _label(x, color, label):  # noqa: ARG001
        ax = plt.gca()
        median_log = np.log1p(subset.loc[subset["primaryLanguage"] == label, "mergedPullRequests"].median())
        ax.text(
            0.02, 0.35, label, fontsize=13, fontweight="bold",
            color="#333", transform=ax.transAxes,
        )
        ax.axvline(median_log, color="#c9302c", linewidth=1.4, linestyle="--", alpha=0.9)

    grid.map(_label, "log_prs")

    grid.figure.subplots_adjust(hspace=-0.35)
    grid.set_titles("")
    grid.set(yticks=[], ylabel="")
    grid.despine(bottom=True, left=True)

    # Rotula o eixo X do subplot inferior com valores reais (não log)
    bottom_ax = grid.axes.flatten()[-1]
    tick_positions = np.log1p([0, 10, 100, 1_000, 10_000, 100_000])
    bottom_ax.set_xticks(tick_positions)
    bottom_ax.set_xticklabels(["0", "10", "100", "1k", "10k", "100k"])
    bottom_ax.set_xlabel("Pull requests aceitos (escala log)")

    grid.figure.suptitle(
        f"Distribuição de PRs aceitos pelas {top_n} linguagens mais frequentes",
        fontsize=14,
        y=1.02,
    )

    _save(grid.figure, _build_path(timestamp, "ridge_prs_by_language"))


# ---------------------------------------------------------------------------
# 4. Timeline de createdAt
# ---------------------------------------------------------------------------
def plot_timeline_created_at(df: pd.DataFrame, timestamp: str) -> None:
    """Distribuição anual de nascimento dos repositórios populares."""
    years = pd.to_datetime(df["createdAt"], utc=True, errors="coerce").dt.year.dropna().astype(int)
    counts = years.value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(12, 5))
    bars = ax.bar(counts.index, counts.values, color=ACCENT, edgecolor="#8a6a1e", linewidth=0.8)

    peak_year = int(counts.idxmax())
    peak_value = int(counts.max())
    for bar, year in zip(bars, counts.index):
        if year == peak_year:
            bar.set_color("#d95f02")
            bar.set_edgecolor("#7a3402")

    ax.set_title(
        "Nascimento dos repositórios populares por ano",
        fontsize=14,
        pad=14,
    )
    ax.set_xlabel("Ano de criação")
    ax.set_ylabel("Número de repositórios")
    ax.set_xticks(counts.index)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

    ax.axhline(counts.median(), color="#555", linestyle=":", linewidth=1, alpha=0.7,
               label=f"Mediana anual: {counts.median():.0f} repos")
    ax.annotate(
        f"Pico: {peak_year} ({peak_value} repos)",
        xy=(peak_year, peak_value),
        xytext=(peak_year + 1.5, peak_value + 6),
        fontsize=11,
        arrowprops=dict(arrowstyle="->", color="#555", lw=1),
    )
    ax.legend(loc="upper right", frameon=False)
    ax.grid(axis="y", alpha=0.3)
    ax.grid(axis="x", visible=False)

    fig.tight_layout()
    _save(fig, _build_path(timestamp, "timeline_created_at"))


# ---------------------------------------------------------------------------
# 5. Scatter idade x PRs com linha de tendência (visualização do Spearman)
# ---------------------------------------------------------------------------
def plot_spearman_scatter(df: pd.DataFrame, timestamp: str) -> None:
    """Scatter de ageInDays x mergedPullRequests com linha de mediana por decis."""
    subset = df[["ageInDays", "mergedPullRequests"]].dropna().copy()
    subset = subset[subset["mergedPullRequests"] > 0]  # log requer > 0

    rho, p_value = stats.spearmanr(subset["ageInDays"], subset["mergedPullRequests"])

    # Medianas por decis de idade para representar tendência de forma robusta
    subset["age_decile"] = pd.qcut(subset["ageInDays"], q=10, duplicates="drop")
    trend = (
        subset.groupby("age_decile", observed=True)
        .agg(age_mid=("ageInDays", "median"), prs_median=("mergedPullRequests", "median"))
        .reset_index(drop=True)
    )

    fig, ax = plt.subplots(figsize=(11, 6.5))

    ax.scatter(
        subset["ageInDays"],
        subset["mergedPullRequests"],
        alpha=0.35,
        s=22,
        color=ACCENT,
        edgecolors="none",
        label=f"Repositórios (n = {len(subset)})",
    )
    ax.plot(
        trend["age_mid"],
        trend["prs_median"],
        color="#c9302c",
        linewidth=2.6,
        marker="o",
        markersize=7,
        markerfacecolor="white",
        markeredgecolor="#c9302c",
        markeredgewidth=1.8,
        label="Mediana de PRs por decil de idade",
    )

    ax.set_yscale("log")
    ax.set_xlabel("Idade do repositório (dias)")
    ax.set_ylabel("Pull requests aceitos (escala log)")
    ax.set_title(
        "Correlação entre idade e PRs aceitos (Teste de Spearman)",
        fontsize=14,
        pad=14,
    )

    # Anotar estatísticas do teste no canto do gráfico
    stats_text = (
        f"Spearman ρ = {rho:.3f}\n"
        f"p-value = {p_value:.2e}\n"
        f"α = 0,05 → H₀ rejeitada"
    )
    ax.text(
        0.02,
        0.97,
        stats_text,
        transform=ax.transAxes,
        fontsize=11,
        verticalalignment="top",
        family="monospace",
        bbox=dict(boxstyle="round,pad=0.6", facecolor="white", edgecolor="#999", alpha=0.9),
    )

    ax.legend(loc="lower right", frameon=True, framealpha=0.9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    _save(fig, _build_path(timestamp, "spearman_scatter"))


# ---------------------------------------------------------------------------
# 6. Boxplot + ECDFs de Maduros vs Jovens (visualização do Mann-Whitney)
# ---------------------------------------------------------------------------
def plot_mann_whitney_comparison(df: pd.DataFrame, timestamp: str) -> None:
    """Painel duplo para o Mann-Whitney: boxplot pareado (esq.) e ECDFs (dir.)."""
    subset = df[["ageInDays", "closedIssuesRatio"]].dropna().copy()
    median_age = subset["ageInDays"].median()

    subset["grupo"] = subset["ageInDays"].apply(
        lambda d: "Maduros" if d > median_age else "Jovens"
    )

    maduros = subset.loc[subset["grupo"] == "Maduros", "closedIssuesRatio"].values
    jovens = subset.loc[subset["grupo"] == "Jovens", "closedIssuesRatio"].values

    u_stat, p_value = stats.mannwhitneyu(maduros, jovens, alternative="two-sided")

    colors = {"Maduros": "#4c72b0", "Jovens": "#dd8452"}

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # --- Painel (a): Boxplot pareado ---
    ax = axes[0]
    box_data = [maduros, jovens]
    labels = [f"Maduros\n(n = {len(maduros)})", f"Jovens\n(n = {len(jovens)})"]
    bp = ax.boxplot(
        box_data,
        tick_labels=labels,
        patch_artist=True,
        widths=0.55,
        medianprops=dict(color="black", linewidth=2),
        flierprops=dict(marker="o", markersize=4, markerfacecolor="gray", alpha=0.5),
    )
    for patch, group in zip(bp["boxes"], ["Maduros", "Jovens"]):
        patch.set_facecolor(colors[group])
        patch.set_alpha(0.75)

    # Anotar medianas sobre as caixas
    for i, (group, values) in enumerate(zip(["Maduros", "Jovens"], box_data), start=1):
        med = float(np.median(values))
        ax.annotate(
            f"mediana = {med:.4f}",
            xy=(i, med),
            xytext=(i + 0.25, med),
            fontsize=10,
            va="center",
            color="#333",
        )

    ax.set_ylabel("Razão de issues fechadas")
    ax.set_title("(a) Boxplot pareado", fontsize=13, pad=10)
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, axis="y", alpha=0.3)

    # --- Painel (b): ECDFs sobrepostas ---
    ax = axes[1]
    for group, values in zip(["Maduros", "Jovens"], [maduros, jovens]):
        sorted_vals = np.sort(values)
        y = np.arange(1, len(sorted_vals) + 1) / len(sorted_vals)
        ax.step(
            sorted_vals,
            y,
            where="post",
            color=colors[group],
            linewidth=2.2,
            label=f"{group} (n = {len(values)})",
        )

    ax.set_xlabel("Razão de issues fechadas")
    ax.set_ylabel("Proporção acumulada")
    ax.set_title("(b) ECDFs sobrepostas", fontsize=13, pad=10)
    ax.set_xlim(0, 1.02)
    ax.set_ylim(0, 1.02)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left", frameon=True, framealpha=0.9)

    # Anotar estatísticas do teste no painel direito
    stats_text = (
        f"Mann-Whitney U = {u_stat:.0f}\n"
        f"p-value = {p_value:.2e}\n"
        f"α = 0,05 → H₀ rejeitada"
    )
    ax.text(
        0.98,
        0.05,
        stats_text,
        transform=ax.transAxes,
        fontsize=10.5,
        verticalalignment="bottom",
        horizontalalignment="right",
        family="monospace",
        bbox=dict(boxstyle="round,pad=0.6", facecolor="white", edgecolor="#999", alpha=0.9),
    )

    fig.suptitle(
        f"Razão de issues fechadas: Maduros vs. Jovens (corte na mediana de idade = {median_age:.0f} dias)",
        fontsize=14,
        y=1.02,
    )
    fig.tight_layout()

    _save(fig, _build_path(timestamp, "mann_whitney_comparison"))


# ---------------------------------------------------------------------------
# Execução principal
# ---------------------------------------------------------------------------
def main() -> None:
    df = load_dataset()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"Gerando gráficos com timestamp {timestamp}...")
    plot_correlation_heatmap(df, timestamp)
    plot_qq_prs(df, timestamp)
    plot_ridge_prs_by_language(df, timestamp)
    plot_timeline_created_at(df, timestamp)
    plot_spearman_scatter(df, timestamp)
    plot_mann_whitney_comparison(df, timestamp)
    print("Concluído.")


if __name__ == "__main__":
    main()
