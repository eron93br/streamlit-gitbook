"""Laboratório 16 — Dashboard de Vendas completo, em um arquivo.

Este é o projeto do Capítulo 16 reunido em um único script, comentado etapa
por etapa. Em um projeto real, separe em `dados.py`, `graficos.py` e `app.py`
(veja `templates/advanced.py`).

Execute na raiz do repositório:
    streamlit run part6/labs/ch16_lab.py
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ==========================================================================
# ETAPA 1 · Configuração da página — SEMPRE o primeiro comando Streamlit
# ==========================================================================
st.set_page_config(
    page_title="Dashboard de Vendas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

RAIZ = Path(__file__).resolve().parents[2]
CSV = RAIZ / "data" / "vendas.csv"

CORES = px.colors.qualitative.Safe
LAYOUT = dict(margin=dict(t=50, b=0, l=0, r=0), height=380,
              legend=dict(orientation="h", y=-0.2, title=""))


# ==========================================================================
# ETAPA 2 · Carga de dados com cache
# ==========================================================================
@st.cache_data(show_spinner="Carregando dados…")
def carregar(caminho: Path) -> pd.DataFrame:
    """Lê o CSV, converte tipos e deriva colunas de apoio.

    As derivações ficam AQUI, dentro do cache, para não serem recalculadas
    a cada rerun.
    """
    df = pd.read_csv(caminho, parse_dates=["data"])
    df["ano"] = df["data"].dt.year
    df["mes"] = df["data"].dt.to_period("M").dt.to_timestamp()
    df["margem"] = df["lucro"] / df["receita"]
    return df


@st.cache_data
def agregar_mensal(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("mes", as_index=False).agg(
        receita=("receita", "sum"),
        lucro=("lucro", "sum"),
        unidades=("unidades", "sum"),
        pedidos=("receita", "size"),
    )


# ==========================================================================
# ETAPA 5 · Os gráficos, como funções puras
# ==========================================================================
def g_evolucao(mensal: pd.DataFrame):
    fig = px.line(mensal, x="mes", y=["receita", "lucro"], markers=True,
                  color_discrete_sequence=CORES,
                  labels={"mes": "", "value": "R$", "variable": ""},
                  title="Evolução mensal")
    fig.update_layout(hovermode="x unified", **LAYOUT)
    return fig


def g_categoria(df: pd.DataFrame):
    dados = df.groupby(["categoria", "canal"], as_index=False)["receita"].sum()
    fig = px.bar(dados, x="receita", y="categoria", color="canal",
                 orientation="h", barmode="group",
                 color_discrete_sequence=CORES,
                 labels={"receita": "Receita (R$)", "categoria": "", "canal": ""},
                 title="Receita por categoria e canal")
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, **LAYOUT)
    return fig


def g_produtos(df: pd.DataFrame):
    dados = df.groupby(["produto", "categoria"], as_index=False).agg(
        receita=("receita", "sum"), unidades=("unidades", "sum"),
        margem=("margem", "mean"))
    fig = px.scatter(dados, x="unidades", y="receita", size="margem",
                     color="categoria", hover_name="produto",
                     color_discrete_sequence=CORES,
                     labels={"unidades": "Unidades vendidas",
                             "receita": "Receita (R$)"},
                     title="Volume × receita por produto")
    fig.update_layout(**LAYOUT)
    return fig


def g_mapa_calor(df: pd.DataFrame):
    tabela = df.pivot_table(index="regiao", columns="categoria",
                            values="receita", aggfunc="sum")
    fig = px.imshow(tabela, text_auto=".2s", aspect="auto",
                    color_continuous_scale="Reds",
                    labels=dict(color="Receita"),
                    title="Receita por região e categoria")
    fig.update_layout(coloraxis_showscale=False, **LAYOUT)
    return fig


# ==========================================================================
# Cabeçalho
# ==========================================================================
st.title("📊 Dashboard de Vendas")

if not CSV.exists():
    st.error(
        "Dataset não encontrado. Rode na raiz do repositório:\n\n"
        "```bash\npython scripts/gerar_dados.py\n```"
    )
    st.stop()

df = carregar(CSV)

st.caption(
    f"Análise comercial · dados sintéticos · {len(df):,} registros · "
    f"{df['data'].min():%d/%m/%Y} a {df['data'].max():%d/%m/%Y}"
)


# ==========================================================================
# ETAPA 3 · Filtros na sidebar
# ==========================================================================
def aplicar_filtros(df, regioes, categorias, canais, periodo):
    mask = (
        df["regiao"].isin(regioes)
        & df["categoria"].isin(categorias)
        & df["canal"].isin(canais)
    )
    if isinstance(periodo, (tuple, list)) and len(periodo) == 2:
        inicio, fim = periodo
        mask &= df["data"].between(pd.Timestamp(inicio), pd.Timestamp(fim))
    return df[mask]


with st.sidebar:
    st.header("Filtros")

    regioes = st.multiselect("Região", sorted(df["regiao"].unique()),
                             default=sorted(df["regiao"].unique()))
    categorias = st.multiselect("Categoria", sorted(df["categoria"].unique()),
                                default=sorted(df["categoria"].unique()))
    canais = st.multiselect("Canal", sorted(df["canal"].unique()),
                            default=sorted(df["canal"].unique()))

    d_min, d_max = df["data"].min().date(), df["data"].max().date()
    periodo = st.date_input("Período", value=(d_min, d_max),
                            min_value=d_min, max_value=d_max)

    st.divider()
    if st.button("🔄 Limpar cache e recarregar", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.caption("Fonte: `scripts/gerar_dados.py`")

filtrado = aplicar_filtros(df, regioes, categorias, canais, periodo)

# Estado vazio tratado ANTES de qualquer cálculo ou gráfico
if filtrado.empty:
    st.warning("Nenhum registro corresponde aos filtros. Amplie a seleção.")
    st.stop()


# ==========================================================================
# ETAPA 4 · A linha de KPIs
# ==========================================================================
def kpis(dados: pd.DataFrame) -> dict:
    receita = dados["receita"].sum()
    lucro = dados["lucro"].sum()
    return {
        "receita": receita,
        "lucro": lucro,
        "margem": lucro / receita if receita else 0.0,
        "ticket": receita / len(dados) if len(dados) else 0.0,
        "custo": dados["custo"].sum(),
    }


ultimo_ano = int(filtrado["ano"].max())
atual = kpis(filtrado[filtrado["ano"] == ultimo_ano])
anterior = kpis(filtrado[filtrado["ano"] == ultimo_ano - 1])


def delta(chave: str) -> str | None:
    if not anterior[chave]:
        return None
    return f"{atual[chave] / anterior[chave] - 1:+.1%}"


st.subheader(f"Indicadores · {ultimo_ano}")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Receita", f"R$ {atual['receita']:,.0f}", delta("receita"), border=True)
k2.metric("Lucro", f"R$ {atual['lucro']:,.0f}", delta("lucro"), border=True)
k3.metric(
    "Margem", f"{atual['margem']:.1%}",
    f"{(atual['margem'] - anterior['margem']) * 100:+.1f} p.p."
    if anterior["margem"] else None,
    border=True,
    help="Variação de métricas percentuais é expressa em pontos percentuais.",
)
k4.metric("Ticket médio", f"R$ {atual['ticket']:,.0f}", delta("ticket"), border=True)
k5.metric("Custo", f"R$ {atual['custo']:,.0f}", delta("custo"),
          delta_color="inverse", border=True,   # ← subir custo é ruim
          help="`delta_color='inverse'`: aumento de custo aparece em vermelho.")

st.caption(f"Comparação com {ultimo_ano - 1}.")
st.divider()

# ==========================================================================
# ETAPA 5 · Gráficos em grade e abas
# ==========================================================================
esq, dir_ = st.columns([3, 2], gap="large")
with esq:
    st.plotly_chart(g_evolucao(agregar_mensal(filtrado)), use_container_width=True)
with dir_:
    st.plotly_chart(g_categoria(filtrado), use_container_width=True)

aba_prod, aba_reg = st.tabs(["🧴 Produtos", "🗺️ Região × Categoria"])
with aba_prod:
    st.plotly_chart(g_produtos(filtrado), use_container_width=True)
with aba_reg:
    st.plotly_chart(g_mapa_calor(filtrado), use_container_width=True)

st.divider()

# ==========================================================================
# ETAPA 6 · Detalhamento, download e acabamento
# ==========================================================================
with st.expander("📋 Detalhamento por produto"):
    detalhe = (
        filtrado.groupby(["categoria", "produto"], as_index=False)
        .agg(receita=("receita", "sum"), lucro=("lucro", "sum"),
             unidades=("unidades", "sum"), satisfacao=("satisfacao", "mean"))
        .sort_values("receita", ascending=False)
    )
    detalhe["margem_pct"] = (detalhe["lucro"] / detalhe["receita"] * 100).round(1)

    st.dataframe(
        detalhe, use_container_width=True, hide_index=True,
        column_config={
            "categoria": "Categoria",
            "produto": "Produto",
            "receita": st.column_config.NumberColumn("Receita", format="R$ %.0f"),
            "lucro": st.column_config.NumberColumn("Lucro", format="R$ %.0f"),
            "unidades": st.column_config.NumberColumn("Unid.", format="%d"),
            "margem_pct": st.column_config.ProgressColumn(
                "Margem", format="%.1f%%", min_value=0, max_value=60),
            "satisfacao": st.column_config.NumberColumn("Satisf.", format="%.1f ⭐"),
        },
    )

    st.download_button(
        "⬇️ Baixar detalhamento (CSV)",
        detalhe.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"detalhamento_{ultimo_ano}.csv",
        mime="text/csv",
    )

with st.expander("📖 Metodologia"):
    st.markdown(
        """
- **Receita** — soma de `unidades × preço unitário`.
- **Lucro** — receita menos custo direto; não inclui despesas indiretas.
- **Margem** — lucro dividido pela receita; variação em pontos percentuais.
- **Ticket médio** — receita dividida pelo número de pedidos.
- **Satisfação** — média das notas de 1 a 5; ~1,5% dos registros são nulos e
  são ignorados no cálculo da média.
"""
    )
    st.latex(r"\text{margem} = \frac{\text{receita} - \text{custo}}{\text{receita}}")
    st.caption("Fonte: dados sintéticos gerados por `scripts/gerar_dados.py`.")

st.caption(
    f"{len(filtrado):,} de {len(df):,} registros exibidos "
    f"({len(filtrado) / len(df):.0%}) · dados até "
    f"{df['data'].max():%d/%m/%Y}"
)
