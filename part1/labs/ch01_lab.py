"""Laboratório 01 — Por que Streamlit?

O menor dashboard útil possível: título, um filtro, um número e um gráfico.
As três seções reproduzem os três passos do capítulo.

Execute na raiz do repositório:
    streamlit run part1/labs/ch01_lab.py
"""

from pathlib import Path

import pandas as pd
import streamlit as st

RAIZ = Path(__file__).resolve().parents[2]
CSV = RAIZ / "data" / "vendas.csv"

st.set_page_config(page_title="Lab 01 · Por que Streamlit", page_icon="📊",
                   layout="wide")

# --------------------------------------------------------------------------
# Passo 1 · O menor app possível
# --------------------------------------------------------------------------
st.title("📊 Lab 01 — O menor dashboard possível")
st.write(
    "Se você está lendo isto no navegador, o Streamlit está funcionando. "
    "As três seções abaixo são os três passos do Capítulo 1."
)
st.divider()

# --------------------------------------------------------------------------
# Passo 2 · Um dado e um controle
# --------------------------------------------------------------------------
st.header("2 · Um dado e um controle")

exemplo = pd.DataFrame(
    {"mes": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"],
     "receita": [120, 145, 98, 176, 131, 189]}
)

limite = st.slider("Receita mínima (mil R$)", 0, 200, 100, step=10)
recorte = exemplo[exemplo["receita"] >= limite]

col_a, col_b = st.columns([1, 2])
col_a.metric("Meses acima do limite", f"{len(recorte)} de {len(exemplo)}")
col_b.bar_chart(recorte.set_index("mes"))

st.caption(
    "Arraste o slider. O número e o gráfico mudam juntos porque o script "
    "**inteiro** foi reexecutado com o novo valor de `limite`."
)
st.divider()

# --------------------------------------------------------------------------
# Passo 3 · O mesmo, com dados reais
# --------------------------------------------------------------------------
st.header("3 · O mesmo padrão, com o dataset do livro")

if not CSV.exists():
    st.error(
        "Dataset não encontrado. Rode na raiz do repositório:\n\n"
        "```bash\npython scripts/gerar_dados.py\n```"
    )
    st.stop()

df = pd.read_csv(CSV, parse_dates=["data"])

regiao = st.selectbox("Região", ["Todas", *sorted(df["regiao"].unique())])
filtrado = df if regiao == "Todas" else df[df["regiao"] == regiao]

k1, k2, k3 = st.columns(3)
k1.metric("Receita", f"R$ {filtrado['receita'].sum():,.0f}".replace(",", "."))
k2.metric("Pedidos", f"{len(filtrado):,}".replace(",", "."))
k3.metric("Ticket médio", f"R$ {filtrado['receita'].mean():,.0f}".replace(",", "."))

st.bar_chart(
    filtrado.groupby("categoria")["receita"].sum().sort_values(),
    horizontal=True,
)

with st.expander("👀 Ver o código desta seção"):
    st.code(
        '''df = pd.read_csv("data/vendas.csv", parse_dates=["data"])

regiao = st.selectbox("Região", ["Todas", *sorted(df["regiao"].unique())])
filtrado = df if regiao == "Todas" else df[df["regiao"] == regiao]

st.metric("Receita", f"R$ {filtrado['receita'].sum():,.0f}")
st.bar_chart(filtrado.groupby("categoria")["receita"].sum())''',
        language="python",
    )

st.caption(
    "Sete linhas úteis: um filtro funcional, um indicador e um gráfico — "
    "servidos em uma URL. É esse o argumento do Streamlit."
)
