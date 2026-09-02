"""Laboratório 11 — Cache e performance, medidos.

Compara a mesma operação com e sem cache, cronometrando cada etapa do
pipeline. Mexa em qualquer widget para forçar reruns e ver a diferença.

Execute na raiz do repositório:
    streamlit run part4/labs/ch11_lab.py
"""

import time
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Lab 11 · Cache", page_icon="⚡", layout="wide")

RAIZ = Path(__file__).resolve().parents[2]
CSV = RAIZ / "data" / "vendas.csv"

if not CSV.exists():
    st.error("Rode `python scripts/gerar_dados.py` na raiz do repositório.")
    st.stop()

LATENCIA = 1.2  # segundos de I/O simulado


# ==========================================================================
# As duas versões da mesma função
# ==========================================================================
def carregar_sem_cache(caminho: Path) -> pd.DataFrame:
    time.sleep(LATENCIA)                      # simula I/O lento
    return pd.read_csv(caminho, parse_dates=["data"])


@st.cache_data
def carregar_com_cache(caminho: Path) -> pd.DataFrame:
    time.sleep(LATENCIA)
    return pd.read_csv(caminho, parse_dates=["data"])


@st.cache_data
def agregar_mensal(df: pd.DataFrame, metrica: str) -> pd.DataFrame:
    """Agregação cacheada POR MÉTRICA — trocar de métrica calcula uma vez só."""
    time.sleep(0.5)                           # simula agregação cara
    return df.groupby(pd.Grouper(key="data", freq="MS"),
                      as_index=False)[metrica].sum()


# ==========================================================================
st.title("⚡ Lab 11 — Cache e performance")

st.session_state.setdefault("historico", [])
st.session_state.setdefault("reruns", 0)
st.session_state.reruns += 1

with st.sidebar:
    st.header("Controles")
    st.slider("Mexa aqui para forçar reruns", 0, 100, 50, key="gatilho")
    metrica = st.selectbox("Métrica", ["receita", "lucro", "unidades", "custo"])
    st.divider()
    if st.button("🔄 Limpar todo o cache", use_container_width=True):
        st.cache_data.clear()
        st.session_state.historico = []
        st.rerun()
    st.caption(f"Reruns nesta sessão: **{st.session_state.reruns}**")

# --------------------------------------------------------------------------
st.header("1 · A mesma leitura, com e sem cache")

col_sem, col_com = st.columns(2, gap="large")

with col_sem:
    t0 = time.perf_counter()
    carregar_sem_cache(CSV)
    dur_sem = time.perf_counter() - t0
    st.metric("❌ Sem cache", f"{dur_sem:.2f} s", border=True)
    st.caption("Paga a latência completa em **todo** rerun.")

with col_com:
    t0 = time.perf_counter()
    df = carregar_com_cache(CSV)
    dur_com = time.perf_counter() - t0
    st.metric("✅ Com `@st.cache_data`", f"{dur_com * 1000:.1f} ms", border=True)
    st.caption("Paga a latência apenas na primeira execução.")

if dur_com > 0:
    st.success(f"Ganho neste rerun: **{dur_sem / dur_com:,.0f}×** mais rápido.")

st.session_state.historico.append(
    {"rerun": st.session_state.reruns,
     "sem_cache_ms": round(dur_sem * 1000, 1),
     "com_cache_ms": round(dur_com * 1000, 2)}
)
st.session_state.historico = st.session_state.historico[-25:]

hist = pd.DataFrame(st.session_state.historico).set_index("rerun")
st.line_chart(hist, height=220)
st.caption(
    "Mexa no slider da barra lateral algumas vezes. A linha sem cache fica "
    "estável no alto; a com cache cai para perto de zero a partir do 2º rerun."
)

st.divider()

# --------------------------------------------------------------------------
st.header("2 · Cachear a agregação, não só a leitura")

t0 = time.perf_counter()
mensal = agregar_mensal(df, metrica)
dur_agg = time.perf_counter() - t0

c1, c2 = st.columns([1, 3])
c1.metric(f"Agregação · {metrica}", f"{dur_agg * 1000:.1f} ms", border=True)
c1.caption(
    "Troque a métrica: a primeira vez custa ~500 ms; ao voltar para uma métrica "
    "já calculada, o custo é ~0. O cache é **por combinação de argumentos**."
)

fig = px.line(mensal, x="data", y=metrica, markers=True,
              labels={"data": "", metrica: metrica.capitalize()})
fig.update_layout(height=300, margin=dict(t=20, b=0, l=0, r=0),
                  hovermode="x unified")
c2.plotly_chart(fig, use_container_width=True)

st.divider()

# --------------------------------------------------------------------------
st.header("3 · `cache_data` vs. `cache_resource`")

st.markdown(
    """
| | `st.cache_data` | `st.cache_resource` |
| --- | --- | --- |
| **Para** | DataFrames, listas, dicts, arrays | Conexões, modelos, clientes de API |
| **Armazena** | uma cópia serializada | o próprio objeto, compartilhado |
| **Cada chamada devolve** | uma cópia nova | a mesma instância |
| **Mutar afeta as outras sessões?** | Não | **Sim** |
"""
)

st.code(
    '''@st.cache_data(ttl="15m", max_entries=20, show_spinner="Consultando…")
def consultar_vendas(_conexao, inicio, fim) -> pd.DataFrame:
    # o prefixo _ faz o Streamlit ignorar esse argumento no hash
    return pd.read_sql(query, _conexao, params=(inicio, fim))


@st.cache_resource
def conexao():
    from sqlalchemy import create_engine
    return create_engine(st.secrets["db"]["url"], pool_pre_ping=True)''',
    language="python",
)

st.warning(
    "⚠️ Ao ignorar um argumento com `_`, você assume a responsabilidade: se o "
    "objeto ignorado mudar, o cache **não** perceberá."
)

st.divider()

# --------------------------------------------------------------------------
st.header("4 · Checklist de desempenho")

itens = [
    "Cacheie a carga de dados (`read_csv` / `read_sql`)",
    "Cacheie também as agregações caras, não só a leitura",
    "Filtre cedo, agregue depois",
    "Não cacheie o que é trivial — o hash tem custo",
    "Use `st.fragment` para isolar reruns de painéis pesados",
    "Use `st.form` para adiar o rerun de filtros múltiplos",
    "Limite as linhas exibidas (`df.head(1000)`)",
    "Prefira Parquet a CSV para volumes grandes",
    "Meça antes de otimizar (`time.perf_counter`)",
]
for item in itens:
    st.checkbox(item, key=f"chk_{item[:20]}")
