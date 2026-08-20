"""Dashboard Streamlit com métricas e gráficos das RQ01 a RQ07."""

import sys

import pandas as pd
import streamlit as st

# analysis.py imprime caracteres como "ρ" (rho), que não existem no
# encoding padrão do console do Windows (cp1252) e quebram o print.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from analysis import load_dataset, test_kruskal_wallis, test_mann_whitney, test_spearman
from metrics import extract_rq07_metrics

st.set_page_config(page_title="RQs — Repositórios Populares", layout="wide")
st.title("Características de repositórios populares — RQ01 a RQ07")

try:
    df = load_dataset()
except FileNotFoundError:
    st.error(
        "Nenhum CSV encontrado em `data/output/`. Rode `python src/main.py` "
        "para coletar os dados antes de abrir o dashboard."
    )
    st.stop()


def histogram(series: pd.Series, bins: int = 10) -> pd.Series:
    """Conta valores por bin e usa o ponto médio como índice numérico,
    para que o gráfico de barras ordene o eixo X corretamente."""
    counts = pd.cut(series.dropna(), bins=bins).value_counts().sort_index()
    counts.index = [round(interval.mid, 1) for interval in counts.index]
    return counts


def show_metric_section(title: str, column: str, as_pct: bool = False) -> None:
    st.subheader(title)
    series = df[column]
    col1, col2 = st.columns(2)
    if as_pct:
        col1.metric("Mediana", f"{series.median():.2%}")
        col2.metric("Média", f"{series.mean():.2%}")
    else:
        col1.metric("Mediana", f"{series.median():.1f}")
        col2.metric("Média", f"{series.mean():.1f}")
    st.bar_chart(histogram(series))


show_metric_section("RQ01 — Idade do repositório (dias)", "ageInDays")
show_metric_section("RQ02 — Pull requests aceitas", "mergedPullRequests")
show_metric_section("RQ03 — Total de releases", "totalReleases")
show_metric_section("RQ04 — Dias desde a última atualização", "timeSinceLastUpdate")

st.subheader("RQ05 — Linguagem primária")
top_languages = df["primaryLanguage"].value_counts().head(10)
st.bar_chart(top_languages)

show_metric_section("RQ06 — Razão de issues fechadas", "closedIssuesRatio", as_pct=True)

st.subheader("RQ07 — Métricas médias por linguagem (top 3)")
top3_langs = df["primaryLanguage"].value_counts().head(3).index.tolist()
rq07_metrics = extract_rq07_metrics(df.to_dict("records"))
rq07_top3 = pd.DataFrame(
    {lang: rq07_metrics[lang] for lang in top3_langs if lang in rq07_metrics}
).T

# Gráficos separados por métrica: cada uma tem uma escala bem diferente
# (PRs na casa dos milhares, releases nas dezenas, dias em unidades) —
# um único gráfico empilhado deixaria as menores praticamente invisíveis.
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("Média de PRs aceitas")
    st.bar_chart(rq07_top3["avgMergedPullRequests"])
with col2:
    st.caption("Média de releases")
    st.bar_chart(rq07_top3["avgTotalReleases"])
with col3:
    st.caption("Média de dias desde a última atualização")
    st.bar_chart(rq07_top3["avgTimeSinceLastUpdate"])


# Realça os cards de teste (st.container(border=True)) com sombra e cantos
# mais suaves — testid estável usado pelo Streamlit para esse componente.
st.markdown(
    """
    <style>
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div.test-card-marker) {
        border-radius: 14px;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
        padding: 4px 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def show_test_card(
    icon: str, title: str, hypothesis: str, stats: dict[str, str], p_value: float
) -> None:
    with st.container(border=True):
        st.markdown('<div class="test-card-marker"></div>', unsafe_allow_html=True)
        header_col, badge_col = st.columns([4, 2])
        header_col.markdown(f"##### {icon} {title}")
        with badge_col:
            st.markdown("<div style='height: 6px'></div>", unsafe_allow_html=True)
            if p_value < 0.05:
                st.badge("Significativo (p < 0.05)", icon="✅", color="green")
            else:
                st.badge("Não significativo (p ≥ 0.05)", icon="⚠️", color="orange")
        st.caption(hypothesis)
        st.divider()
        cols = st.columns(len(stats) + 1)
        for col, (label, value) in zip(cols, stats.items()):
            col.metric(label, value)
        cols[-1].metric("p-value", f"{p_value:.4g}")


st.header("Testes estatísticos")

spearman = test_spearman(df)
show_test_card(
    "📈",
    "Teste 1 — Correlação de Spearman",
    "H0: não há correlação entre idade do repositório e PRs aceitas",
    {"Coeficiente (ρ)": f"{spearman['spearman_rho']:.4f}"},
    spearman["spearman_p_value"],
)

mann_whitney = test_mann_whitney(df)
show_test_card(
    "⚖️",
    "Teste 2 — Mann-Whitney U",
    "H0: repositórios Maduros e Jovens têm a mesma razão de issues fechadas",
    {
        "Mediana (Maduros)": f"{mann_whitney['mediana_razao_maduros']:.2%}",
        "Mediana (Jovens)": f"{mann_whitney['mediana_razao_jovens']:.2%}",
    },
    mann_whitney["mann_whitney_p_value"],
)

kruskal = test_kruskal_wallis(df, top3_langs=top3_langs)
show_test_card(
    "📊",
    "Teste 3 — Kruskal-Wallis H",
    f"H0: PRs aceitas têm a mesma distribuição entre {', '.join(top3_langs)}",
    {"H-statistic": f"{kruskal['kruskal_wallis_h']:.4f}"},
    kruskal["kruskal_wallis_p_value"],
)
