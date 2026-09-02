"""Template BÁSICO de dashboard Streamlit — uma página.

Ponto de partida para um dashboard focado, de público único.
Estrutura: config → carga cacheada → filtros → KPIs → gráficos → tabela.

COMO ADAPTAR AO SEU PROJETO (nesta ordem):
    1. CAMINHO_DADOS e a função `carregar()`
    2. Os filtros da sidebar → suas colunas categóricas e sua coluna de data
    3. A função `kpis()` → suas métricas
    4. As funções `g_*()` → seus gráficos

Uso:
    cp templates/basic.py meu_projeto/app.py
    streamlit run app.py
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------------------------------
# CONFIGURAÇÃO — st.set_page_config precisa ser o primeiro comando Streamlit
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Meu Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

CAMINHO_DADOS = Path(__file__).resolve().parents[1] / "data" / "vendas.csv"

CORES = px.colors.qualitative.Safe
LAYOUT = dict(margin=dict(t=50, b=0, l=0, r=0), height=380,
              legend=dict(orientation="h", y=-0.2, title=""))


# --------------------------------------------------------------------------
# DADOS — toda operação cara vai para dentro do cache
# --------------------------------------------------------------------------
@st.cache_data(show_spinner="Carregando dados…")
def carregar(caminho: Path) -> pd.DataFrame:
    df = pd.read_csv(caminho, parse_dates=["data"])
    df["mes"] = df["data"].dt.to_period("M").dt.to_timestamp()
    return df


# --------------------------------------------------------------------------
# GRÁFICOS — uma função por figura, recebendo o DataFrame já filtrado
# --------------------------------------------------------------------------
def g_evolucao(df: pd.DataFrame):
    mensal = df.groupby("mes", as_index=False)[["receita", "lucro"]].sum()
    fig = px.line(mensal, x="mes", y=["receita", "lucro"], markers=True,
                  color_discrete_sequence=CORES,
                  labels={"mes": "", "value": "R$", "variable": ""},
                  title="Evolução mensal")
    fig.update_layout(hovermode="x unified", **LAYOUT)
    return fig


def g_categoria(df: pd.DataFrame):
    dados = df.groupby("categoria", as_index=False)["receita"].sum()
    fig = px.bar(dados, x="receita", y="categoria", orientation="h",
                 color_discrete_sequence=CORES,
                 labels={"receita": "Receita (R$)", "categoria": ""},
                 title="Receita por categoria")
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, **LAYOUT)
    return fig


# --------------------------------------------------------------------------
# APP
# --------------------------------------------------------------------------
st.title("📊 Meu Dashboard")

if not CAMINHO_DADOS.exists():
    st.error(f"Dataset não encontrado em `{CAMINHO_DADOS}`.")
    st.stop()

df = carregar(CAMINHO_DADOS)
st.caption(
    f"{len(df):,} registros · {df['data'].min():%d/%m/%Y} a "
    f"{df['data'].max():%d/%m/%Y}"
)

# --- FILTROS (sidebar) ---
with st.sidebar:
    st.header("Filtros")
    regioes = st.multiselect("Região", sorted(df["regiao"].unique()),
                             default=sorted(df["regiao"].unique()))
    categorias = st.multiselect("Categoria", sorted(df["categoria"].unique()),
                                default=sorted(df["categoria"].unique()))
    d_min, d_max = df["data"].min().date(), df["data"].max().date()
    periodo = st.date_input("Período", value=(d_min, d_max),
                            min_value=d_min, max_value=d_max)

mask = df["regiao"].isin(regioes) & df["categoria"].isin(categorias)
if isinstance(periodo, (tuple, list)) and len(periodo) == 2:
    mask &= df["data"].between(pd.Timestamp(periodo[0]), pd.Timestamp(periodo[1]))
filtrado = df[mask]

# --- ESTADO VAZIO (antes de qualquer cálculo) ---
if filtrado.empty:
    st.warning("Nenhum registro corresponde aos filtros. Amplie a seleção.")
    st.stop()

# --- KPIs ---
k1, k2, k3, k4 = st.columns(4)
k1.metric("Receita", f"R$ {filtrado['receita'].sum():,.0f}", border=True)
k2.metric("Lucro", f"R$ {filtrado['lucro'].sum():,.0f}", border=True)
k3.metric("Margem",
          f"{filtrado['lucro'].sum() / filtrado['receita'].sum():.1%}", border=True)
k4.metric("Ticket médio", f"R$ {filtrado['receita'].mean():,.0f}", border=True)

st.divider()

# --- GRÁFICOS ---
esq, dir_ = st.columns([3, 2], gap="large")
esq.plotly_chart(g_evolucao(filtrado), use_container_width=True)
dir_.plotly_chart(g_categoria(filtrado), use_container_width=True)

# --- TABELA E DOWNLOAD ---
with st.expander("📋 Dados detalhados"):
    st.dataframe(
        filtrado.head(500), use_container_width=True, hide_index=True,
        column_config={
            "data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
            "receita": st.column_config.NumberColumn("Receita", format="R$ %.2f"),
            "lucro": st.column_config.NumberColumn("Lucro", format="R$ %.2f"),
        },
    )
    st.download_button(
        "⬇️ Baixar CSV",
        filtrado.to_csv(index=False).encode("utf-8-sig"),
        file_name="recorte.csv",
        mime="text/csv",
    )

st.caption(
    f"{len(filtrado):,} de {len(df):,} registros exibidos "
    f"({len(filtrado) / len(df):.0%})."
)
