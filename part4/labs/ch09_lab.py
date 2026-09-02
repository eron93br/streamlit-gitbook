"""Laboratório 09 — Catálogo de widgets + painel de filtros funcional.

Execute na raiz do repositório:
    streamlit run part4/labs/ch09_lab.py
"""

from datetime import date, time as dtime
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Lab 09 · Widgets", page_icon="🎛️", layout="wide")

RAIZ = Path(__file__).resolve().parents[2]
CSV = RAIZ / "data" / "vendas.csv"

if not CSV.exists():
    st.error("Rode `python scripts/gerar_dados.py` na raiz do repositório.")
    st.stop()


@st.cache_data
def carregar() -> pd.DataFrame:
    return pd.read_csv(CSV, parse_dates=["data"])


df = carregar()

st.title("🎛️ Lab 09 — Widgets de input")

aba_painel, aba_catalogo, aba_form = st.tabs(
    ["1 · Painel de filtros", "2 · Catálogo de widgets", "3 · Formulário"]
)

# ==========================================================================
# 1 · Painel de filtros funcional
# ==========================================================================
with aba_painel:
    st.header("Painel de filtros sobre o dataset de vendas")
    st.caption("Convenção: filtros na sidebar, resultados na área principal.")

    def limpar_filtros():
        """Callback: roda ANTES do rerun, por isso pode escrever no state."""
        st.session_state.f_regiao = sorted(df["regiao"].unique())
        st.session_state.f_categoria = sorted(df["categoria"].unique())
        st.session_state.f_canal = "Todos"

    with st.sidebar:
        st.header("Filtros")
        st.button("↺ Limpar filtros", on_click=limpar_filtros,
                  use_container_width=True)

        regioes = st.multiselect(
            "Região", sorted(df["regiao"].unique()),
            default=sorted(df["regiao"].unique()),
            key="f_regiao",
            help="Deixe vazio para não filtrar por região.",
        )
        categorias = st.multiselect(
            "Categoria", sorted(df["categoria"].unique()),
            default=sorted(df["categoria"].unique()),
            key="f_categoria",
        )
        canal = st.radio("Canal", ["Todos", *sorted(df["canal"].unique())],
                         key="f_canal")

        d_min, d_max = df["data"].min().date(), df["data"].max().date()
        periodo = st.date_input("Período", value=(d_min, d_max),
                                min_value=d_min, max_value=d_max)

        teto = int(df["receita"].max())
        ticket = st.slider("Valor do pedido (R$)", 0, teto, (0, teto), step=250)

        st.divider()
        mostrar_tabela = st.toggle("Mostrar tabela detalhada", value=False)

    # --- aplicação dos filtros: máscara booleana acumulada ---
    mask = pd.Series(True, index=df.index)
    if regioes:
        mask &= df["regiao"].isin(regioes)
    if categorias:
        mask &= df["categoria"].isin(categorias)
    if canal != "Todos":
        mask &= df["canal"] == canal
    if isinstance(periodo, (tuple, list)) and len(periodo) == 2:
        mask &= df["data"].between(pd.Timestamp(periodo[0]), pd.Timestamp(periodo[1]))
    mask &= df["receita"].between(*ticket)

    filtrado = df[mask]

    if filtrado.empty:
        st.warning("Nenhum registro corresponde aos filtros. Amplie a seleção.")
        st.stop()

    st.caption(
        f"**{len(filtrado):,}** de {len(df):,} registros "
        f"({len(filtrado) / len(df):.0%} da base)."
    )

    k1, k2, k3 = st.columns(3)
    k1.metric("Receita", f"R$ {filtrado['receita'].sum():,.0f}", border=True)
    k2.metric("Lucro", f"R$ {filtrado['lucro'].sum():,.0f}", border=True)
    k3.metric("Ticket médio", f"R$ {filtrado['receita'].mean():,.0f}", border=True)

    mensal = filtrado.groupby(pd.Grouper(key="data", freq="MS"),
                              as_index=False)["receita"].sum()
    fig = px.line(mensal, x="data", y="receita", markers=True,
                  labels={"data": "", "receita": "Receita (R$)"})
    fig.update_layout(height=340, margin=dict(t=20, b=0, l=0, r=0),
                      hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    if mostrar_tabela:
        st.dataframe(filtrado.head(500), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Filtros dependentes")
    st.caption(
        "As opções do segundo widget dependem do primeiro. Nenhum callback é "
        "necessário — o script roda de cima para baixo."
    )
    c1, c2 = st.columns(2)
    cat_sel = c1.selectbox("Categoria", sorted(df["categoria"].unique()))
    produtos = sorted(df.loc[df["categoria"] == cat_sel, "produto"].unique())
    prod_sel = c2.selectbox("Produto", produtos)
    st.metric(
        f"Receita de {prod_sel}",
        f"R$ {df.loc[df['produto'] == prod_sel, 'receita'].sum():,.0f}",
    )

# ==========================================================================
# 2 · Catálogo
# ==========================================================================
with aba_catalogo:
    st.header("Catálogo de widgets")
    st.caption("Cada widget com o valor que retorna, ao lado.")

    def linha(rotulo: str, valor):
        st.caption(f"↳ retorna: `{valor!r}`  ·  tipo: `{type(valor).__name__}`")
        st.divider()

    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.subheader("Booleanos e ações")
        linha("checkbox", st.checkbox("st.checkbox", value=True))
        linha("toggle", st.toggle("st.toggle", value=False))
        linha("button", st.button("st.button"))
        st.link_button("st.link_button", "https://docs.streamlit.io")
        st.divider()

        st.subheader("Escolha única")
        linha("radio", st.radio("st.radio", ["A", "B", "C"], horizontal=True))
        linha("selectbox", st.selectbox("st.selectbox", ["Opção 1", "Opção 2"]))
        linha("select_slider",
              st.select_slider("st.select_slider",
                               options=["Baixo", "Médio", "Alto"], value="Médio"))

        st.subheader("Escolha múltipla")
        linha("multiselect",
              st.multiselect("st.multiselect", ["X", "Y", "Z"], default=["X"]))

    with c2:
        st.subheader("Números")
        linha("slider", st.slider("st.slider", 0, 100, 42))
        linha("slider (faixa)", st.slider("st.slider — faixa", 0, 100, (20, 80)))
        linha("number_input", st.number_input("st.number_input", value=3.14, step=0.1))

        st.subheader("Texto")
        linha("text_input", st.text_input("st.text_input", placeholder="Digite algo"))
        linha("text_area", st.text_area("st.text_area", height=80))

        st.subheader("Data, hora e cor")
        linha("date_input", st.date_input("st.date_input", value=date(2025, 1, 1)))
        linha("time_input", st.time_input("st.time_input", value=dtime(9, 30)))
        linha("color_picker", st.color_picker("st.color_picker", "#FF4B4B"))

        st.subheader("Arquivo e avaliação")
        arquivo = st.file_uploader("st.file_uploader", type=["csv", "png", "jpg"])
        st.caption(f"↳ retorna: `{arquivo.name if arquivo else None}`")
        linha("feedback", st.feedback("stars"))

# ==========================================================================
# 3 · Formulário
# ==========================================================================
with aba_form:
    st.header("`st.form` — adiar o rerun")
    st.caption(
        "Dentro do formulário, nenhum widget dispara rerun. Tudo é enviado de "
        "uma vez no clique do `form_submit_button`."
    )

    with st.form("filtros_form"):
        f1, f2 = st.columns(2)
        r = f1.multiselect("Regiões", sorted(df["regiao"].unique()),
                           default=sorted(df["regiao"].unique()))
        c = f2.multiselect("Canais", sorted(df["canal"].unique()),
                           default=sorted(df["canal"].unique()))
        faixa = st.slider("Ticket (R$)", 0, int(df["receita"].max()),
                          (0, int(df["receita"].max())), step=250)
        comentario = st.text_input("Comentário (opcional)")

        enviado = st.form_submit_button("Aplicar filtros", type="primary",
                                        use_container_width=True)

    if enviado:
        sub = df[
            df["regiao"].isin(r)
            & df["canal"].isin(c)
            & df["receita"].between(*faixa)
        ]
        st.success(f"Filtros aplicados: {len(sub):,} registros.")
        if comentario:
            st.caption(f"Comentário registrado: _{comentario}_")
        st.bar_chart(sub.groupby("categoria")["receita"].sum())
    else:
        st.info("Ajuste os campos e clique em **Aplicar filtros**.")

    st.divider()
    st.warning(
        "**Quando não usar form:** quando o cálculo é rápido e o usuário espera "
        "ver o efeito de cada ajuste imediatamente. O form troca resposta "
        "instantânea por menos recálculo."
    )
