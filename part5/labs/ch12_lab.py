"""Laboratório 12 — O mesmo conteúdo em quatro layouts.

Execute na raiz do repositório:
    streamlit run part5/labs/ch12_lab.py
"""

import time
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Lab 12 · Layouts", page_icon="🧱", layout="wide")

RAIZ = Path(__file__).resolve().parents[2]
CSV = RAIZ / "data" / "vendas.csv"

if not CSV.exists():
    st.error("Rode `python scripts/gerar_dados.py` na raiz do repositório.")
    st.stop()


@st.cache_data
def carregar() -> pd.DataFrame:
    return pd.read_csv(CSV, parse_dates=["data"])


df = carregar()

LAYOUT = dict(height=320, margin=dict(t=40, b=0, l=0, r=0),
              legend=dict(orientation="h", y=-0.2, title=""))


@st.cache_data
def fig_evolucao(dados: pd.DataFrame):
    mensal = dados.groupby(pd.Grouper(key="data", freq="MS"),
                           as_index=False)[["receita", "lucro"]].sum()
    fig = px.line(mensal, x="data", y=["receita", "lucro"], markers=True,
                  labels={"data": "", "value": "R$", "variable": ""},
                  title="Evolução mensal")
    fig.update_layout(hovermode="x unified", **LAYOUT)
    return fig


@st.cache_data
def fig_categoria(dados: pd.DataFrame):
    agrup = dados.groupby("categoria", as_index=False)["receita"].sum()
    fig = px.bar(agrup, x="receita", y="categoria", orientation="h",
                 labels={"receita": "Receita (R$)", "categoria": ""},
                 title="Receita por categoria")
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, **LAYOUT)
    return fig


@st.cache_data
def fig_canal(dados: pd.DataFrame):
    agrup = dados.groupby("canal", as_index=False)["receita"].sum()
    fig = px.pie(agrup, names="canal", values="receita", hole=0.55,
                 title="Participação por canal")
    fig.update_layout(**LAYOUT)
    return fig


kpis = {
    "Receita": f"R$ {df['receita'].sum():,.0f}",
    "Lucro": f"R$ {df['lucro'].sum():,.0f}",
    "Ticket médio": f"R$ {df['receita'].mean():,.0f}",
    "Satisfação": f"{df['satisfacao'].mean():.2f} / 5",
}

st.title("🧱 Lab 12 — Layouts e containers")
st.caption("O mesmo conteúdo arranjado de quatro formas. Compare a legibilidade.")

a1, a2, a3, a4, a5 = st.tabs(
    ["1 · Empilhado", "2 · Colunas", "3 · Abas", "4 · Grade completa",
     "5 · Outros containers"]
)

# ==========================================================================
with a1:
    st.header("Sem containers: tudo empilhado")
    st.error("❌ Quatro KPIs empilhados já ocupam a tela inteira.")
    for rotulo, valor in kpis.items():
        st.metric(rotulo, valor)
    st.plotly_chart(fig_evolucao(df), use_container_width=True, key="e1")
    st.plotly_chart(fig_categoria(df), use_container_width=True, key="c1")

# ==========================================================================
with a2:
    st.header("`st.columns`: KPIs em linha")
    cols = st.columns(len(kpis))
    for col, (rotulo, valor) in zip(cols, kpis.items()):
        col.metric(rotulo, valor, border=True)

    st.divider()
    esq, dir_ = st.columns([2, 1], gap="large")
    esq.plotly_chart(fig_evolucao(df), use_container_width=True, key="e2")
    dir_.plotly_chart(fig_canal(df), use_container_width=True, key="k2")

    st.code(
        '''cols = st.columns(4)                 # quatro colunas iguais
esq, dir_ = st.columns([2, 1])       # a esquerda tem o dobro da largura
a, b = st.columns(2, gap="large", border=True)''',
        language="python",
    )

# ==========================================================================
with a3:
    st.header("`st.tabs`: visões alternativas")
    t1, t2, t3 = st.tabs(["📈 Evolução", "📊 Categorias", "🥧 Canais"])
    t1.plotly_chart(fig_evolucao(df), use_container_width=True, key="e3")
    t2.plotly_chart(fig_categoria(df), use_container_width=True, key="c3")
    t3.plotly_chart(fig_canal(df), use_container_width=True, key="k3")

    st.warning(
        "⚠️ O conteúdo de **todas** as abas é executado a cada rerun — o "
        "Streamlit apenas esconde visualmente. Se cada aba faz um cálculo "
        "pesado, o custo é a soma de todos. Combine com `st.cache_data` "
        "(como aqui) ou `st.fragment`."
    )

# ==========================================================================
with a4:
    st.header("A grade de um dashboard real")
    st.caption("Contexto → números → tendência e composição → detalhe.")

    # Placeholder no topo, preenchido no fim do bloco
    topo = st.empty()

    cols = st.columns(len(kpis))
    for col, (rotulo, valor) in zip(cols, kpis.items()):
        col.metric(rotulo, valor, border=True)

    esq, dir_ = st.columns([3, 2], gap="large")
    esq.plotly_chart(fig_evolucao(df), use_container_width=True, key="e4")
    dir_.plotly_chart(fig_categoria(df), use_container_width=True, key="c4")

    with st.expander("📋 Detalhamento (sob demanda)"):
        st.dataframe(
            df.nlargest(50, "receita")[
                ["data", "regiao", "categoria", "produto", "canal", "receita"]
            ],
            use_container_width=True, hide_index=True,
            column_config={
                "data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
                "receita": st.column_config.NumberColumn("Receita", format="R$ %.2f"),
            },
        )

    # o placeholder é preenchido agora, mas aparece lá em cima
    topo.info(
        f"📊 {len(df):,} registros · período de "
        f"{df['data'].min():%d/%m/%Y} a {df['data'].max():%d/%m/%Y}"
    )

    st.code(
        '''topo = st.empty()        # reserva o lugar no fluxo
# ... 200 linhas de processamento ...
topo.info("resumo calculado no fim, exibido no topo")''',
        language="python",
    )

# ==========================================================================
with a5:
    st.header("Outros containers")

    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.subheader("`st.container(border=True, height=...)`")
        with st.container(border=True, height=240):
            st.markdown("**Top 10 produtos**")
            st.dataframe(
                df.groupby("produto")["receita"].sum().nlargest(10),
                use_container_width=True,
            )
        st.caption("`height` cria rolagem interna, sem alongar a página.")

        st.subheader("`st.popover`")
        with st.popover("⚙️ Opções do gráfico"):
            st.checkbox("Suavizar série")
            st.slider("Janela (meses)", 1, 12, 3)
            st.radio("Escala", ["Linear", "Log"], horizontal=True)
        st.caption("Não ocupa espaço quando fechado — é um botão.")

    with c2:
        st.subheader("`st.expander`")
        with st.expander("📖 Metodologia"):
            st.markdown(
                "- **Receita**: `unidades × preço unitário`\n"
                "- **Lucro**: receita − custo direto\n"
                "- **Margem**: lucro / receita"
            )
        st.caption("Ocupa uma linha de título quando fechado.")

        st.subheader("`st.dialog` — modal")

        @st.dialog("Detalhes do período")
        def modal():
            st.metric("Receita total", f"R$ {df['receita'].sum():,.0f}")
            st.metric("Registros", f"{len(df):,}")
            st.caption("Modais interrompem o fluxo — use com parcimônia.")
            if st.button("Fechar"):
                st.rerun()

        if st.button("Abrir modal"):
            modal()

        st.subheader("`st.empty` em loop")
        if st.button("▶️ Rodar contagem"):
            ph = st.empty()
            for i in range(1, 6):
                ph.metric("Processando", f"{i}/5")
                time.sleep(0.35)
            ph.success("Concluído!")
