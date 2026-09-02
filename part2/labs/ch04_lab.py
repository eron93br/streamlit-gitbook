"""Laboratório 04 — st.write, magic commands e funções específicas.

Galeria dos tipos que o `st.write` reconhece, e comparação lado a lado entre
`st.write`, magic e a função de display específica.

Execute na raiz do repositório:
    streamlit run part2/labs/ch04_lab.py
"""

import time
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Lab 04 · write e magic", page_icon="✍️",
                   layout="wide")

RAIZ = Path(__file__).resolve().parents[2]
CSV = RAIZ / "data" / "vendas.csv"

if not CSV.exists():
    st.error("Rode `python scripts/gerar_dados.py` na raiz do repositório.")
    st.stop()

df = pd.read_csv(CSV, parse_dates=["data"])
resumo = (
    df.groupby("regiao", as_index=False)["receita"].sum()
      .sort_values("receita", ascending=False)
)

st.title("✍️ Lab 04 — `st.write`, magic e funções específicas")

# ==========================================================================
aba1, aba2, aba3 = st.tabs(
    ["1 · Três caminhos", "2 · Galeria de tipos", "3 · write_stream"]
)

# --------------------------------------------------------------------------
with aba1:
    st.header("O mesmo objeto, três renderizações")

    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.subheader("`st.write`")
        st.caption("Adivinha o tipo e delega.")
        st.write(resumo)
        st.code("st.write(resumo)", language="python")

    with c2:
        st.subheader("magic")
        st.caption("A variável sozinha na linha.")
        resumo  # ← isto é um magic command
        st.code("resumo  # a variável sozinha", language="python")

    with c3:
        st.subheader("`st.dataframe`")
        st.caption("Controle explícito da apresentação.")
        st.dataframe(
            resumo,
            use_container_width=True,
            hide_index=True,
            column_config={
                "regiao": "Região",
                "receita": st.column_config.NumberColumn(
                    "Receita", format="R$ %.0f"
                ),
            },
        )
        st.code(
            'st.dataframe(resumo, hide_index=True,\n'
            '             column_config={...})',
            language="python",
        )

    st.info(
        "**Regra prática:** prototipe com `st.write`; entregue com a função "
        "específica. Só a terceira coluna produz a tabela que você mostraria "
        "para outra pessoa."
    )

# --------------------------------------------------------------------------
with aba2:
    st.header("O que `st.write` faz com cada tipo")

    exemplos = {
        "int / float": 1234.56,
        "str (markdown)": "Texto com **negrito**, :blue[cor] e emoji :sunglasses:",
        "dict": {"chave": "valor", "lista": [1, 2, 3], "aninhado": {"a": 1}},
        "list": ["Nordeste", "Sudeste", "Sul"],
        "pandas.Series": df.groupby("canal")["receita"].sum(),
        "pandas.DataFrame": resumo.head(3),
    }

    for rotulo, objeto in exemplos.items():
        esq, dir_ = st.columns([1, 3], gap="medium", vertical_alignment="top")
        esq.markdown(f"**{rotulo}**")
        with dir_:
            st.write(objeto)
        st.divider()

    st.markdown("**Figura Plotly**")
    fig = px.bar(resumo, x="regiao", y="receita",
                 labels={"regiao": "", "receita": "Receita (R$)"})
    fig.update_layout(height=300, margin=dict(t=20, b=0, l=0, r=0))
    st.write(fig)   # equivale a st.plotly_chart(fig)
    st.caption("`st.write(fig)` funciona, mas não aceita `use_container_width`.")

    st.markdown("**Múltiplos argumentos**")
    st.write("Região líder:", resumo.iloc[0]["regiao"], "→",
             f"R$ {resumo.iloc[0]['receita']:,.2f}")

# --------------------------------------------------------------------------
with aba3:
    st.header("`st.write_stream` — saída incremental")
    st.caption(
        "Consome um gerador e escreve conforme os pedaços chegam. "
        "Típico de respostas de modelos de linguagem."
    )

    def gerar_analise():
        texto = (
            f"A região líder é **{resumo.iloc[0]['regiao']}**, com "
            f"R$ {resumo.iloc[0]['receita']:,.0f} de receita acumulada, "
            f"o que representa "
            f"{resumo.iloc[0]['receita'] / resumo['receita'].sum():.1%} do total. "
            "A última colocada é "
            f"**{resumo.iloc[-1]['regiao']}**."
        )
        for palavra in texto.split(" "):
            yield palavra + " "
            time.sleep(0.03)

    if st.button("▶️ Gerar análise", type="primary"):
        completo = st.write_stream(gerar_analise)
        st.divider()
        st.caption("A função **retorna** o texto completo ao final:")
        st.code(completo, language="text")
