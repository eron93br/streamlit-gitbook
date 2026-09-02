"""Laboratório 10 — Session state, rerun, fragmentos e query params.

Execute na raiz do repositório:
    streamlit run part4/labs/ch10_lab.py
"""

from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Lab 10 · Session state", page_icon="🧠",
                   layout="wide")

RAIZ = Path(__file__).resolve().parents[2]
CSV = RAIZ / "data" / "vendas.csv"

if not CSV.exists():
    st.error("Rode `python scripts/gerar_dados.py` na raiz do repositório.")
    st.stop()


@st.cache_data
def carregar() -> pd.DataFrame:
    return pd.read_csv(CSV, parse_dates=["data"])


df = carregar()

st.title("🧠 Lab 10 — Session state e o ciclo de rerun")

a1, a2, a3, a4 = st.tabs(
    ["1 · Contador", "2 · Carrinho", "3 · URL e reset", "4 · Fragmento"]
)

# ==========================================================================
with a1:
    st.header("Local vs. session_state")

    st.session_state.setdefault("cliques", 0)

    local = 0
    if st.button("Clique aqui", type="primary"):
        st.session_state.cliques += 1
        local += 1

    c1, c2 = st.columns(2)
    c1.metric("`st.session_state.cliques`", st.session_state.cliques, border=True)
    c2.metric("variável local", local, border=True)

    st.caption(
        "O primeiro acumula porque mora fora do escopo do script. O segundo é "
        "recriado do zero a cada rerun e nunca passa de 1."
    )

    st.code(
        '''st.session_state.setdefault("cliques", 0)

local = 0
if st.button("Clique aqui"):
    st.session_state.cliques += 1   # persiste
    local += 1                      # some no próximo rerun''',
        language="python",
    )

# ==========================================================================
with a2:
    st.header("Acumulando uma lista: carrinho")

    st.session_state.setdefault("carrinho", [])

    c1, c2, c3 = st.columns([2, 1, 1], vertical_alignment="bottom")
    produto = c1.selectbox("Produto", sorted(df["produto"].unique()))
    qtd = c2.number_input("Qtd.", 1, 99, 1)
    preco = float(df.loc[df["produto"] == produto, "preco_unitario"].mean())
    c3.metric("Preço médio", f"R$ {preco:,.2f}")

    b1, b2 = st.columns(2)
    if b1.button("➕ Adicionar", type="primary", use_container_width=True):
        st.session_state.carrinho.append(
            {"produto": produto, "quantidade": int(qtd),
             "preco": round(preco, 2), "total": round(preco * qtd, 2)}
        )
    if b2.button("🗑️ Esvaziar", use_container_width=True):
        st.session_state.carrinho = []

    if st.session_state.carrinho:
        carrinho = pd.DataFrame(st.session_state.carrinho)
        st.dataframe(
            carrinho, use_container_width=True, hide_index=True,
            column_config={
                "produto": "Produto",
                "quantidade": st.column_config.NumberColumn("Qtd.", format="%d"),
                "preco": st.column_config.NumberColumn("Preço", format="R$ %.2f"),
                "total": st.column_config.NumberColumn("Total", format="R$ %.2f"),
            },
        )
        st.metric("Total do carrinho", f"R$ {carrinho['total'].sum():,.2f}")
    else:
        st.info("Carrinho vazio. Adicione um produto acima.")

# ==========================================================================
with a3:
    st.header("Estado na URL e reset correto")

    st.subheader("`st.query_params` — estado compartilhável")

    disponiveis = sorted(df["regiao"].unique())
    padrao = st.query_params.get_all("regiao") or disponiveis
    padrao = [r for r in padrao if r in disponiveis] or disponiveis

    selecionadas = st.multiselect("Região (gravada na URL)", disponiveis,
                                  default=padrao, key="q_regiao")
    st.query_params["regiao"] = selecionadas

    sub = df[df["regiao"].isin(selecionadas)] if selecionadas else df
    st.metric("Receita do recorte", f"R$ {sub['receita'].sum():,.0f}")
    st.caption(
        "Olhe a barra de endereços: o recorte está na URL. Copie o link e abra "
        "em outra aba — o dashboard reabre já filtrado. O `session_state`, "
        "diferentemente, morre no F5."
    )

    st.divider()
    st.subheader("Reset pelo caminho certo (callback)")

    def resetar():
        """Roda ANTES do rerun — por isso pode escrever nas chaves dos widgets."""
        st.session_state.r_canal = "Todos"
        st.session_state.r_meta = 50_000
        st.session_state.ultimo_reset = datetime.now().strftime("%H:%M:%S")

    st.button("↺ Resetar", on_click=resetar)
    st.radio("Canal", ["Todos", *sorted(df["canal"].unique())], key="r_canal",
             horizontal=True)
    st.slider("Meta (R$)", 0, 200_000, 50_000, step=5_000, key="r_meta")

    if "ultimo_reset" in st.session_state:
        st.caption(f"Último reset às {st.session_state.ultimo_reset}.")

    st.error(
        "❌ **Não faça isto:** atribuir a `st.session_state.r_meta` **depois** "
        "de o slider ter sido desenhado levanta `StreamlitAPIException`. "
        "A alteração precisa acontecer no callback."
    )

# ==========================================================================
with a4:
    st.header("`st.fragment` — reexecutar só um pedaço")

    st.caption(
        "Trocar o produto abaixo reexecuta apenas o fragmento. O contador de "
        "reruns globais (no rodapé) não se mexe."
    )

    @st.fragment
    def painel_produto(dados: pd.DataFrame):
        st.session_state.setdefault("reruns_fragmento", 0)
        st.session_state.reruns_fragmento += 1

        p = st.selectbox("Produto", sorted(dados["produto"].unique()),
                         key="frag_produto")
        sub = dados[dados["produto"] == p]

        f1, f2, f3 = st.columns(3)
        f1.metric("Receita", f"R$ {sub['receita'].sum():,.0f}")
        f2.metric("Unidades", int(sub["unidades"].sum()))
        f3.metric("Reruns do fragmento", st.session_state.reruns_fragmento)

        mensal = sub.groupby(pd.Grouper(key="data", freq="MS"))["receita"].sum()
        st.line_chart(mensal)

    with st.container(border=True):
        painel_produto(df)

# ==========================================================================
# Rodapé: inspetor do session_state — excelente para depurar
# ==========================================================================
st.session_state.setdefault("reruns_globais", 0)
st.session_state.reruns_globais += 1

st.divider()
with st.expander("🔍 Inspetor do `st.session_state`", expanded=False):
    st.metric("Reruns globais do script", st.session_state.reruns_globais)
    st.json({k: str(v)[:120] for k, v in st.session_state.items()})
    st.caption(
        "Este painel é a ferramenta de depuração mais útil em apps com estado. "
        "Vale copiá-lo para os seus projetos durante o desenvolvimento."
    )
