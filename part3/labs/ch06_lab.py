"""Laboratório 06 — Plotly Express: as figuras empacotadas como funções.

Cada gráfico é uma função que recebe o DataFrame **já filtrado** e devolve uma
figura. É exatamente esse o formato que deve migrar do notebook para o
`graficos.py` do seu projeto.

Execute na raiz do repositório:
    streamlit run part3/labs/ch06_lab.py
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Lab 06 · Plotly Express", page_icon="📈",
                   layout="wide")

RAIZ = Path(__file__).resolve().parents[2]
CSV = RAIZ / "data" / "vendas.csv"

CORES = px.colors.qualitative.Safe
LAYOUT = dict(margin=dict(t=50, b=0, l=0, r=0), height=400,
              legend=dict(orientation="h", y=-0.2, title=""))


# ==========================================================================
# As funções de gráfico — copie estas para o seu graficos.py
# ==========================================================================
def evolucao(df: pd.DataFrame):
    """Linha: receita e lucro agregados por mês."""
    mensal = (
        df.groupby(pd.Grouper(key="data", freq="MS"), as_index=False)
          .agg(receita=("receita", "sum"), lucro=("lucro", "sum"))
    )
    fig = px.line(mensal, x="data", y=["receita", "lucro"], markers=True,
                  color_discrete_sequence=CORES,
                  labels={"data": "", "value": "R$", "variable": ""},
                  title="Receita e lucro por mês")
    fig.update_layout(hovermode="x unified", **LAYOUT)
    return fig


def barras_categoria(df: pd.DataFrame):
    """Barras horizontais agrupadas: receita por categoria e canal."""
    dados = df.groupby(["categoria", "canal"], as_index=False)["receita"].sum()
    fig = px.bar(dados, x="receita", y="categoria", color="canal",
                 orientation="h", barmode="group",
                 color_discrete_sequence=CORES,
                 labels={"receita": "Receita (R$)", "categoria": "", "canal": ""},
                 title="Receita por categoria e canal")
    # Sem esta linha, as barras saem em ordem alfabética e escondem o ranking.
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, **LAYOUT)
    return fig


def dispersao_produtos(df: pd.DataFrame):
    """Dispersão: volume × receita, com margem no tamanho do ponto."""
    dados = df.groupby(["produto", "categoria"], as_index=False).agg(
        receita=("receita", "sum"),
        unidades=("unidades", "sum"),
        satisfacao=("satisfacao", "mean"),
    )
    fig = px.scatter(dados, x="unidades", y="receita", size="satisfacao",
                     color="categoria", hover_name="produto", log_y=True,
                     color_discrete_sequence=CORES,
                     labels={"unidades": "Unidades vendidas",
                             "receita": "Receita (R$, escala log)"},
                     title="Volume × receita por produto")
    fig.update_layout(**LAYOUT)
    return fig


def distribuicao_ticket(df: pd.DataFrame):
    """Histograma: distribuição do ticket por canal."""
    fig = px.histogram(df, x="receita", color="canal", nbins=50,
                       marginal="box", opacity=0.75,
                       color_discrete_sequence=CORES,
                       labels={"receita": "Valor do pedido (R$)",
                               "canal": "", "count": "Pedidos"},
                       title="Distribuição do valor dos pedidos")
    fig.update_layout(barmode="overlay", **LAYOUT)
    return fig


def calor_regiao_categoria(df: pd.DataFrame):
    """Mapa de calor: receita por região e categoria."""
    tabela = df.pivot_table(index="regiao", columns="categoria",
                            values="receita", aggfunc="sum")
    fig = px.imshow(tabela, text_auto=".2s", aspect="auto",
                    color_continuous_scale="Reds",
                    labels=dict(color="Receita"),
                    title="Receita por região e categoria")
    fig.update_layout(coloraxis_showscale=False, **LAYOUT)
    return fig


# ==========================================================================
# O app
# ==========================================================================
st.title("📈 Lab 06 — Cinco figuras, cinco funções")
st.caption(
    "Estas figuras foram estruturadas no notebook antes de virem para cá. "
    "Cada uma é uma função pura: recebe o DataFrame filtrado, devolve a figura."
)

if not CSV.exists():
    st.error("Rode `python scripts/gerar_dados.py` na raiz do repositório.")
    st.stop()

df = pd.read_csv(CSV, parse_dates=["data"])

with st.sidebar:
    st.header("Filtros")
    regioes = st.multiselect("Região", sorted(df["regiao"].unique()),
                             default=sorted(df["regiao"].unique()))
    canais = st.multiselect("Canal", sorted(df["canal"].unique()),
                            default=sorted(df["canal"].unique()))

filtrado = df[df["regiao"].isin(regioes) & df["canal"].isin(canais)]

if filtrado.empty:
    st.warning("Nenhum registro para os filtros selecionados.")
    st.stop()

st.caption(f"{len(filtrado):,} de {len(df):,} registros.")

graficos = {
    "📈 Evolução": (evolucao, "px.line + hovermode='x unified'"),
    "📊 Categorias": (barras_categoria, "px.bar + categoryorder"),
    "🔵 Produtos": (dispersao_produtos, "px.scatter + size + log_y"),
    "📉 Distribuição": (distribuicao_ticket, "px.histogram + marginal='box'"),
    "🔥 Mapa de calor": (calor_regiao_categoria, "px.imshow + pivot_table"),
}

abas = st.tabs(list(graficos))
for aba, (rotulo, (funcao, nota)) in zip(abas, graficos.items()):
    with aba:
        st.plotly_chart(funcao(filtrado), use_container_width=True)
        st.caption(f"`{nota}`")
        with st.expander("👀 Ver o código desta figura"):
            import inspect
            st.code(inspect.getsource(funcao), language="python")

st.divider()
st.info(
    "**Como usar no seu projeto:** copie estas funções para um `graficos.py` "
    "e, no `app.py`, escreva uma linha por gráfico:\n\n"
    "```python\nst.plotly_chart(evolucao(filtrado), use_container_width=True)\n```"
)
