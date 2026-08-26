"""Dashboard Streamlit com métricas, gráficos e testes estatísticos das RQ01 a RQ07."""

import sys
from contextlib import contextmanager
from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st

# analysis.py imprime caracteres como "ρ" (rho), que não existem no
# encoding padrão do console do Windows (cp1252) e quebram o print.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from analysis import DATA_DIR, load_dataset, test_kruskal_wallis, test_mann_whitney, test_spearman
from metrics import extract_rq07_metrics

ACCENT = "#e3b341"
SURFACE = "#12181f"
BORDER = "#232b33"
TEXT = "#e6edf3"
MUTED = "#8b98a5"

# Cores reais do GitHub Linguist — cada linguagem "veste" sua cor oficial
# nos gráficos, em vez de uma barra azul genérica.
LANGUAGE_COLORS = {
    "Python": "#3572A5",
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "Go": "#00ADD8",
    "Rust": "#dea584",
    "Java": "#b07219",
    "C++": "#f34b7d",
    "C": "#555555",
    "C#": "#178600",
    "Shell": "#89e051",
    "Jupyter Notebook": "#DA5B0B",
    "Ruby": "#701516",
    "PHP": "#4F5D95",
    "Swift": "#F05138",
    "Kotlin": "#A97BFF",
    "Objective-C": "#438eff",
    "Scala": "#c22d40",
    "HTML": "#e34c26",
    "Vue": "#41b883",
    "Elixir": "#6e4a7e",
}
DEFAULT_LANGUAGE_COLOR = "#6e7681"

st.set_page_config(page_title="RQs — Repositórios Populares", layout="wide", page_icon="⭐")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

    html, body, [class*="st-emotion"], [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'IBM Plex Mono', monospace !important;
        letter-spacing: -0.01em;
    }

    [data-testid="stSidebar"] {
        background: #12181f;
        border-right: 1px solid #232b33;
    }
    [data-testid="stSidebar"] a {
        color: #8b98a5 !important;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.85rem;
        text-decoration: none;
    }
    [data-testid="stSidebar"] a:hover {
        color: #e3b341 !important;
    }

    [data-testid="stMetricValue"] {
        font-family: 'IBM Plex Mono', monospace;
    }
    [data-testid="stMetricLabel"] {
        font-family: 'IBM Plex Sans', sans-serif;
        color: #e3b341 !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-size: 0.72rem !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:has(> div > div.app-card-marker) {
        background: #12181f;
        border: 1px solid #232b33 !important;
        border-radius: 14px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.35);
        padding: 0.4rem 0.6rem;
    }

    .eyebrow {
        font-family: 'IBM Plex Mono', monospace;
        color: #e3b341;
        font-size: 0.78rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin: 2.2rem 0 0.4rem;
    }

    hr {
        border-color: #232b33 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

try:
    df = load_dataset()
except FileNotFoundError:
    st.error(
        "Nenhum CSV encontrado em `data/output/`. Rode `python src/main.py` "
        "para coletar os dados antes de abrir o dashboard."
    )
    st.stop()

latest_csv = sorted(DATA_DIR.glob("repositories_*.csv"))[-1]
collected_at = datetime.strptime(latest_csv.stem.split("_", 1)[1], "%Y%m%d_%H%M%S")

SECTIONS = [
    ("rq01", "RQ01"),
    ("rq02", "RQ02"),
    ("rq03", "RQ03"),
    ("rq04", "RQ04"),
    ("rq05", "RQ05"),
    ("rq06", "RQ06"),
    ("rq07", "RQ07"),
    ("testes", "Testes"),
]
with st.sidebar:
    st.markdown(
        "<div style='font-family:IBM Plex Mono, monospace; font-weight:600; "
        "color:#e6edf3; font-size:0.95rem; margin-bottom:0.8rem;'>"
        "⭐ Lab01 — Sumário</div>",
        unsafe_allow_html=True,
    )
    for anchor_id, label in SECTIONS:
        st.markdown(f"[{label}](#{anchor_id})")


def style_chart(chart: alt.Chart) -> alt.Chart:
    return (
        chart.properties(height=260, background="transparent")
        .configure_view(strokeWidth=0)
        .configure_axis(labelColor=MUTED, titleColor=MUTED, gridColor=BORDER, domainColor=BORDER)
    )


def language_chart(series: pd.Series, y_title: str) -> alt.Chart:
    data = series.reset_index()
    data.columns = ["language", "value"]
    domain = data["language"].tolist()
    colors = [LANGUAGE_COLORS.get(lang, DEFAULT_LANGUAGE_COLOR) for lang in domain]
    chart = (
        alt.Chart(data)
        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X("language:N", sort=domain, title=None, axis=alt.Axis(labelAngle=-40)),
            y=alt.Y("value:Q", title=y_title),
            color=alt.Color(
                "language:N", scale=alt.Scale(domain=domain, range=colors), legend=None
            ),
            tooltip=["language", "value"],
        )
    )
    return style_chart(chart)


@contextmanager
def card(anchor_id: str):
    st.markdown(f'<div id="{anchor_id}"></div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<div class="app-card-marker"></div>', unsafe_allow_html=True)
        yield


def histogram(series: pd.Series, bins: int = 10) -> pd.Series:
    """Conta valores por bin e usa o ponto médio como índice numérico,
    para que o gráfico de barras ordene o eixo X corretamente."""
    counts = pd.cut(series.dropna(), bins=bins).value_counts().sort_index()
    counts.index = [round(interval.mid, 1) for interval in counts.index]
    return counts


def show_metric_section(
    anchor_id: str,
    title: str,
    column: str,
    as_pct: bool = False,
    hypothesis: str | None = None,
) -> None:
    with card(anchor_id):
        st.subheader(title, anchor=False)
        series = df[column]
        col1, col2 = st.columns(2)
        if as_pct:
            col1.metric("Mediana", f"{series.median():.2%}")
            col2.metric("Média", f"{series.mean():.2%}")
        else:
            col1.metric("Mediana", f"{series.median():.1f}")
            col2.metric("Média", f"{series.mean():.1f}")
        st.bar_chart(histogram(series), color=ACCENT)
        if hypothesis:
            median_display = f"{series.median():.2%}" if as_pct else f"{series.median():.1f}"
            st.caption(f"**Hipótese (S02):** {hypothesis}")
            st.caption(f"**Resultado observado:** mediana de {median_display}.")


# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------

st.markdown(
    f"""
    <div style="padding: 1.6rem 0 1.2rem;">
      <div style="font-family:'IBM Plex Mono',monospace; color:{MUTED}; font-size:0.8rem;
                  letter-spacing:0.12em; text-transform:uppercase; margin-bottom:0.5rem;">
        ⭐ Lab01 — Laboratório de Experimentação de Software
      </div>
      <div style="font-family:'IBM Plex Mono',monospace; font-weight:700; font-size:2.3rem;
                  color:{TEXT}; line-height:1.2;">
        Características de repositórios <span style="color:{ACCENT};">populares</span>
      </div>
      <div style="font-family:'IBM Plex Sans',sans-serif; color:{MUTED}; font-size:1rem;
                  margin-top:0.6rem; max-width:620px;">
        Evidências estatísticas sobre idade, contribuição, manutenção e linguagem
        dos repositórios mais populares do GitHub — RQ01 a RQ07.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.container(border=True):
    st.markdown('<div class="app-card-marker"></div>', unsafe_allow_html=True)
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Repositórios analisados", f"{len(df):,}".replace(",", "."))
    kpi2.metric(
        "Mediana de estrelas", f"{df['stargazerCount'].median():,.0f}".replace(",", ".")
    )
    kpi3.metric("Coleta em", collected_at.strftime("%d/%m/%Y"))

# ---------------------------------------------------------------------------
# Métricas descritivas
# ---------------------------------------------------------------------------

st.markdown('<div class="eyebrow">Métricas descritivas</div>', unsafe_allow_html=True)

show_metric_section("rq01", "RQ01 — Idade do repositório (dias)", "ageInDays")
show_metric_section("rq02", "RQ02 — Pull requests aceitas", "mergedPullRequests")
show_metric_section("rq03", "RQ03 — Total de releases", "totalReleases")
show_metric_section("rq04", "RQ04 — Dias desde a última atualização", "timeSinceLastUpdate")

# ---------------------------------------------------------------------------
# Linguagens
# ---------------------------------------------------------------------------

st.markdown('<div class="eyebrow">Linguagens</div>', unsafe_allow_html=True)

with card("rq05"):
    st.subheader("RQ05 — Linguagem primária", anchor=False)
    lang_counts = df["primaryLanguage"].value_counts()
    top_languages = lang_counts.head(10)
    st.altair_chart(
        language_chart(top_languages, "Repositórios"), use_container_width=True
    )
    n_valid_lang = df["primaryLanguage"].notna().sum()
    top3_pct = ", ".join(
        f"{lang} ({100 * count / n_valid_lang:.1f}%)"
        for lang, count in lang_counts.head(3).items()
    )
    st.caption(
        "**Hipótese (S02):** a maioria dos repositórios populares é escrita em "
        "linguagens consolidadas de mercado (ex.: Python, JavaScript, Java, C++)."
    )
    st.caption(f"**Resultado observado:** hipótese confirmada — top 3: {top3_pct}.")

show_metric_section(
    "rq06",
    "RQ06 — Razão de issues fechadas",
    "closedIssuesRatio",
    as_pct=True,
    hypothesis=(
        "existe uma alta proporção de issues fechadas em relação ao total, "
        "indicando governança técnica sólida e capacidade de resposta da equipe mantenedora."
    ),
)

with card("rq07"):
    st.subheader("RQ07 — Métricas por linguagem (top 3)", anchor=False)
    top3_langs = df["primaryLanguage"].value_counts().head(3).index.tolist()
    rq07_metrics = extract_rq07_metrics(df.to_dict("records"))
    rq07_top3 = pd.DataFrame(
        {lang: rq07_metrics[lang] for lang in top3_langs if lang in rq07_metrics}
    ).T

    def median_caption(median_column: str) -> str:
        return "Mediana — " + " · ".join(
            f"{lang}: {rq07_top3.loc[lang, median_column]:.1f}"
            for lang in top3_langs
            if lang in rq07_top3.index
        )

    # Gráficos separados por métrica: cada uma tem uma escala bem diferente
    # (PRs na casa dos milhares, releases nas dezenas, dias em unidades) —
    # um único gráfico empilhado deixaria as menores praticamente invisíveis.
    # A mediana é exibida junto (texto) por ser mais robusta a outliers que a média.
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption("Média de PRs aceitas")
        top3_series = rq07_top3["avgMergedPullRequests"]
        top3_series.index.name = None
        st.altair_chart(language_chart(top3_series, ""), use_container_width=True)
        st.caption(median_caption("medianMergedPullRequests"))
    with col2:
        st.caption("Média de releases")
        st.altair_chart(
            language_chart(rq07_top3["avgTotalReleases"], ""), use_container_width=True
        )
        st.caption(median_caption("medianTotalReleases"))
    with col3:
        st.caption("Média de dias desde a última atualização")
        st.altair_chart(
            language_chart(rq07_top3["avgTimeSinceLastUpdate"], ""), use_container_width=True
        )
        st.caption(median_caption("medianTimeSinceLastUpdate"))

    st.divider()
    top_prs_lang = rq07_top3["medianMergedPullRequests"].astype(float).idxmax()
    st.caption(
        "**Hipótese (S02):** projetos escritos nas linguagens mais populares recebem mais "
        "contribuições externas, lançam mais releases e são atualizados com mais frequência."
    )
    st.caption(
        f"**Resultado observado:** parcialmente confirmada — entre as top 3 linguagens, "
        f"{top_prs_lang} concentra a maior mediana de PRs aceitos, mas a liderança em volume "
        "de repositórios (linguagem mais frequente) não coincide necessariamente com a maior "
        "mediana de engajamento por projeto. Ver teste de Kruskal-Wallis abaixo para a "
        "significância estatística da diferença entre linguagens."
    )

# ---------------------------------------------------------------------------
# Testes estatísticos
# ---------------------------------------------------------------------------

st.markdown('<div id="testes"></div>', unsafe_allow_html=True)
st.header("Testes estatísticos", anchor=False)


def show_test_card(
    icon: str, title: str, hypothesis: str, stats: dict[str, str], p_value: float
) -> None:
    with st.container(border=True):
        st.markdown('<div class="app-card-marker"></div>', unsafe_allow_html=True)
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
