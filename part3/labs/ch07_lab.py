"""Laboratório 07 — KPIs, tabelas formatadas, editor e download.

Execute na raiz do repositório:
    streamlit run part3/labs/ch07_lab.py
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Lab 07 · Exibindo dados", page_icon="📋",
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
ano_atual = int(df["data"].dt.year.max())
ano_anterior = ano_atual - 1

st.title("📋 Lab 07 — Exibindo dados")

# ==========================================================================
# 1 · A linha de KPIs
# ==========================================================================
st.header(f"1 · Linha de KPIs · {ano_atual} vs. {ano_anterior}")

atual = df[df["data"].dt.year == ano_atual]
anterior = df[df["data"].dt.year == ano_anterior]


def variacao(valor_atual: float, valor_anterior: float) -> str | None:
    if not valor_anterior:
        return None
    return f"{valor_atual / valor_anterior - 1:+.1%}"


k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Receita", f"R$ {atual['receita'].sum():,.0f}",
          variacao(atual["receita"].sum(), anterior["receita"].sum()),
          border=True)
k2.metric("Lucro", f"R$ {atual['lucro'].sum():,.0f}",
          variacao(atual["lucro"].sum(), anterior["lucro"].sum()),
          border=True)
k3.metric("Unidades", f"{int(atual['unidades'].sum()):,}",
          variacao(atual["unidades"].sum(), anterior["unidades"].sum()),
          border=True)
k4.metric("Ticket médio", f"R$ {atual['receita'].mean():,.0f}",
          variacao(atual["receita"].mean(), anterior["receita"].mean()),
          border=True)
k5.metric("Custo", f"R$ {atual['custo'].sum():,.0f}",
          variacao(atual["custo"].sum(), anterior["custo"].sum()),
          delta_color="inverse",   # ← subir custo é ruim
          border=True)

st.caption(
    "O último KPI usa `delta_color='inverse'`: para custo, um aumento é ruim e "
    "deve aparecer em vermelho."
)
st.divider()

# ==========================================================================
# 2 · Tabela formatada com column_config
# ==========================================================================
st.header("2 · Tabela formatada com `column_config`")

resumo = (
    df.groupby("categoria", as_index=False)
      .agg(receita=("receita", "sum"),
           lucro=("lucro", "sum"),
           unidades=("unidades", "sum"),
           satisfacao=("satisfacao", "mean"))
      .sort_values("receita", ascending=False)
)
resumo["margem_pct"] = (resumo["lucro"] / resumo["receita"] * 100).round(1)

# Sparkline: uma coluna cujo conteúdo é uma LISTA vira um minigráfico.
serie = (
    df.groupby(["categoria", pd.Grouper(key="data", freq="MS")])["receita"]
      .sum()
      .groupby(level=0)
      .apply(list)
      .rename("tendencia")
      .reset_index()
)
resumo = resumo.merge(serie, on="categoria")

cru, formatado = st.tabs(["❌ Sem formatação", "✅ Com `column_config`"])

with cru:
    st.dataframe(resumo.drop(columns="tendencia"), use_container_width=True)
    st.caption("Números crus, índice visível, sem unidades.")

with formatado:
    st.dataframe(
        resumo,
        use_container_width=True,
        hide_index=True,
        column_order=["categoria", "receita", "lucro", "margem_pct",
                      "unidades", "satisfacao", "tendencia"],
        column_config={
            "categoria": st.column_config.TextColumn("Categoria", width="medium"),
            "receita": st.column_config.NumberColumn("Receita", format="R$ %.0f"),
            "lucro": st.column_config.NumberColumn("Lucro", format="R$ %.0f"),
            "margem_pct": st.column_config.ProgressColumn(
                "Margem", format="%.1f%%", min_value=0, max_value=60),
            "unidades": st.column_config.NumberColumn("Unid.", format="%d"),
            "satisfacao": st.column_config.NumberColumn("Satisf.", format="%.1f ⭐"),
            "tendencia": st.column_config.LineChartColumn("Tendência mensal", y_min=0),
        },
    )
    st.caption("Mesma informação. Leitura completamente diferente.")

st.divider()

# ==========================================================================
# 3 · Mestre-detalhe com on_select
# ==========================================================================
st.header("3 · Tabela como filtro (`on_select`)")
st.caption("Selecione uma linha para ver o detalhamento — o padrão mestre-detalhe.")

produtos = (
    df.groupby(["produto", "categoria"], as_index=False)
      .agg(receita=("receita", "sum"), unidades=("unidades", "sum"))
      .sort_values("receita", ascending=False)
)

evento = st.dataframe(
    produtos,
    use_container_width=True,
    hide_index=True,
    height=260,
    on_select="rerun",
    selection_mode="single-row",
    key="tabela_produtos",
    column_config={
        "produto": "Produto",
        "categoria": "Categoria",
        "receita": st.column_config.NumberColumn("Receita", format="R$ %.0f"),
        "unidades": st.column_config.NumberColumn("Unidades", format="%d"),
    },
)

linhas = evento.selection.rows
if linhas:
    nome = produtos.iloc[linhas[0]]["produto"]
    sub = df[df["produto"] == nome]

    st.subheader(f"Detalhe · {nome}")
    d1, d2, d3 = st.columns(3)
    d1.metric("Receita", f"R$ {sub['receita'].sum():,.0f}")
    d2.metric("Pedidos", f"{len(sub):,}")
    d3.metric("Satisfação média", f"{sub['satisfacao'].mean():.2f}")

    mensal = sub.groupby(pd.Grouper(key="data", freq="MS"), as_index=False)["receita"].sum()
    fig = px.line(mensal, x="data", y="receita", markers=True,
                  labels={"data": "", "receita": "Receita (R$)"})
    fig.update_layout(height=280, margin=dict(t=20, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("👆 Clique em uma linha da tabela acima.")

st.divider()

# ==========================================================================
# 4 · data_editor e download
# ==========================================================================
st.header("4 · `st.data_editor` e download")

esq, dir_ = st.columns([3, 2], gap="large")

with esq:
    st.subheader("Simulação de metas")
    premissas = pd.DataFrame({
        "categoria": resumo["categoria"],
        "receita_atual": resumo["receita"].round(0),
        "meta": (resumo["receita"] * 1.1).round(0),
    })

    editado = st.data_editor(
        premissas,
        use_container_width=True,
        hide_index=True,
        disabled=["categoria", "receita_atual"],
        column_config={
            "categoria": "Categoria",
            "receita_atual": st.column_config.NumberColumn("Atual", format="R$ %.0f"),
            "meta": st.column_config.NumberColumn(
                "Meta editável", format="R$ %.0f", min_value=0, step=10000),
        },
    )
    editado = editado.copy()
    editado["gap_pct"] = (
        editado["meta"] / editado["receita_atual"] - 1
    ) * 100

with dir_:
    st.subheader("Resultado da simulação")
    st.metric("Meta total", f"R$ {editado['meta'].sum():,.0f}")
    st.metric("Crescimento necessário",
              f"{editado['meta'].sum() / editado['receita_atual'].sum() - 1:+.1%}")
    st.caption(
        "⚠️ O `data_editor` altera apenas a cópia em memória desta sessão. "
        "Nada é gravado em disco automaticamente."
    )

    st.download_button(
        "⬇️ Baixar simulação (CSV)",
        editado.to_csv(index=False).encode("utf-8-sig"),
        file_name="simulacao_metas.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.caption("`utf-8-sig` garante que os acentos abram corretos no Excel.")
