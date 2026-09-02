"""Laboratório 03 — O modelo de execução (rerun) na prática.

Este app **mostra** o rerun acontecendo: conta as execuções, cronometra cada
uma e compara uma variável local com uma chave do session_state.

Execute na raiz do repositório:
    streamlit run part1/labs/ch03_lab.py
"""

import time
from pathlib import Path

import pandas as pd
import streamlit as st

# 1 · st.set_page_config PRECISA ser o primeiro comando Streamlit do script.
st.set_page_config(
    page_title="Lab 03 · Modelo de execução",
    page_icon="🔁",
    layout="wide",
    initial_sidebar_state="expanded",
)

RAIZ = Path(__file__).resolve().parents[2]
CSV = RAIZ / "data" / "vendas.csv"

inicio_do_rerun = time.perf_counter()

# --------------------------------------------------------------------------
# Contadores: o que sobrevive e o que não sobrevive
# --------------------------------------------------------------------------
st.session_state.setdefault("execucoes", 0)
st.session_state.setdefault("historico_ms", [])
st.session_state.execucoes += 1

contador_local = 0  # ← recriado do zero a cada rerun

st.title("🔁 Lab 03 — Vendo o rerun acontecer")
st.write(
    "Toda interação reexecuta este script do início. Clique no botão várias "
    "vezes e observe a diferença entre os dois contadores."
)

clicou = st.button("Clique aqui", type="primary")
if clicou:
    contador_local += 1

c1, c2, c3 = st.columns(3)
c1.metric("Reruns nesta sessão", st.session_state.execucoes, border=True)
c2.metric("Contador local", contador_local, border=True)
c3.metric("Botão retornou", str(clicou), border=True)

st.caption(
    "O contador de reruns sobe sempre (mora no `session_state`). O contador "
    "local nunca passa de 1 — ele é recriado a cada execução. E o botão só "
    "retorna `True` no rerun causado pelo próprio clique."
)

st.divider()

# --------------------------------------------------------------------------
# st.stop: interromper quando uma pré-condição falha
# --------------------------------------------------------------------------
st.header("Pré-condições com `st.stop`")

if not CSV.exists():
    st.error(
        "Dataset não encontrado. Rode `python scripts/gerar_dados.py` "
        "na raiz do repositório."
    )
    st.stop()  # nada abaixo desta linha é executado

st.success(f"Dataset encontrado em `{CSV.relative_to(RAIZ)}`.")

# --------------------------------------------------------------------------
# A ordem canônica: config → dados → cabeçalho → controles → transformação → saída
# --------------------------------------------------------------------------
st.divider()
st.header("A ordem canônica de um app")

lento = st.sidebar.toggle(
    "Simular carga lenta (1,2s)", value=False,
    help="Ligue e mexa em qualquer widget: todo rerun paga o custo de novo.",
)

if lento:
    time.sleep(1.2)

df = pd.read_csv(CSV, parse_dates=["data"])

with st.sidebar:
    st.header("Controles")
    regiao = st.selectbox("Região", ["Todas", *sorted(df["regiao"].unique())])
    metrica = st.radio("Métrica", ["receita", "lucro", "unidades"], horizontal=True)

filtrado = df if regiao == "Todas" else df[df["regiao"] == regiao]

esq, dir_ = st.columns([2, 1], gap="large")

with esq:
    st.subheader(f"{metrica.capitalize()} por mês · {regiao}")
    mensal = filtrado.groupby(
        pd.Grouper(key="data", freq="MS")
    )[metrica].sum()
    st.line_chart(mensal)

with dir_:
    st.subheader("Resumo")
    st.metric("Registros", f"{len(filtrado):,}".replace(",", "."))
    st.metric(metrica.capitalize(), f"{filtrado[metrica].sum():,.0f}".replace(",", "."))

# --------------------------------------------------------------------------
# Cronômetro do rerun
# --------------------------------------------------------------------------
duracao_ms = (time.perf_counter() - inicio_do_rerun) * 1000
st.session_state.historico_ms.append(round(duracao_ms, 1))
st.session_state.historico_ms = st.session_state.historico_ms[-30:]

st.divider()
st.subheader("⏱️ Duração de cada rerun (ms)")
st.line_chart(pd.Series(st.session_state.historico_ms, name="ms"))
st.caption(
    f"Este rerun levou **{duracao_ms:.1f} ms**. Ligue a carga lenta na barra "
    "lateral e veja o salto — é exatamente esse custo que o `st.cache_data` "
    "elimina (Capítulo 11)."
)
