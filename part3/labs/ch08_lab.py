"""Laboratório 08 — Funções gráficas e mídia.

O mesmo dado desenhado por três níveis de abstração, mais mapa, grafo e imagem.

Execute na raiz do repositório:
    streamlit run part3/labs/ch08_lab.py
"""

import io
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Lab 08 · Funções gráficas", page_icon="🎨",
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
por_cat = (
    df.groupby("categoria", as_index=False)["receita"].sum()
      .sort_values("receita")
)

st.title("🎨 Lab 08 — Funções gráficas e mídia")

# ==========================================================================
st.header("1 · O mesmo dado, três níveis de abstração")

n1, n2, n3 = st.tabs(["Nível 1 · Nativo", "Nível 2 · Plotly", "Nível 3 · Matplotlib"])

with n1:
    st.bar_chart(por_cat, x="categoria", y="receita", horizontal=True)
    st.code('st.bar_chart(por_cat, x="categoria", y="receita", horizontal=True)',
            language="python")
    st.caption(
        "Uma linha. Sem controle de rótulo de eixo, formatação de moeda "
        "ou hover unificado. Ótimo para explorar, insuficiente para entregar."
    )

with n2:
    fig = px.bar(por_cat, x="receita", y="categoria", orientation="h",
                 color_discrete_sequence=px.colors.qualitative.Safe,
                 labels={"receita": "Receita (R$)", "categoria": ""},
                 title="Receita por categoria")
    fig.update_layout(height=360, margin=dict(t=50, b=0, l=0, r=0),
                      yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)
    st.code(
        '''fig = px.bar(por_cat, x="receita", y="categoria", orientation="h",
             labels={"receita": "Receita (R$)", "categoria": ""})
fig.update_layout(height=360, margin=dict(t=50, b=0, l=0, r=0),
                  yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig, use_container_width=True)''',
        language="python")
    st.caption("Interativo, ordenado, rotulado. **O padrão para dashboards.**")

with n3:
    fig_mpl, ax = plt.subplots(figsize=(7, 3.6))
    sns.barplot(data=por_cat, x="receita", y="categoria", ax=ax, color="#ff4b4b")
    ax.set_xlabel("Receita (R$)")
    ax.set_ylabel("")
    fig_mpl.tight_layout()
    st.pyplot(fig_mpl, use_container_width=True)
    st.code(
        '''fig, ax = plt.subplots(figsize=(7, 3.6))   # SEMPRE crie a figura explicitamente
sns.barplot(data=por_cat, x="receita", y="categoria", ax=ax)
fig.tight_layout()
st.pyplot(fig)''',
        language="python")
    st.caption("Estático — sem hover nem zoom — mas com controle total do desenho.")

st.divider()

# ==========================================================================
st.header("2 · Um gráfico estatístico que o Seaborn faz melhor")

esq, dir_ = st.columns(2, gap="large")

with esq:
    fig_box, ax = plt.subplots(figsize=(6, 3.8))
    sns.boxplot(data=df, x="satisfacao", y="categoria", ax=ax,
                palette="Reds", hue="categoria", legend=False)
    ax.set_xlabel("Satisfação (1–5)")
    ax.set_ylabel("")
    fig_box.tight_layout()
    st.pyplot(fig_box, use_container_width=True)
    st.caption("Boxplot da distribuição de satisfação por categoria.")

with dir_:
    fig_corr, ax = plt.subplots(figsize=(6, 3.8))
    corr = df[["unidades", "preco_unitario", "receita", "lucro", "satisfacao"]].corr()
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", center=0, ax=ax,
                cbar=False)
    ax.set_title("Correlação entre variáveis")
    fig_corr.tight_layout()
    st.pyplot(fig_corr, use_container_width=True)
    st.caption("Matriz de correlação anotada.")

st.divider()

# ==========================================================================
st.header("3 · Gráfico como filtro (`on_select`)")

fig_sel = px.bar(por_cat, x="categoria", y="receita",
                 labels={"categoria": "", "receita": "Receita (R$)"})
fig_sel.update_layout(height=300, margin=dict(t=20, b=0, l=0, r=0))

evento = st.plotly_chart(fig_sel, use_container_width=True,
                         on_select="rerun", key="barras_cat")

pontos = evento.selection.get("points", []) if evento and evento.selection else []
if pontos:
    cat = pontos[0]["x"]
    st.subheader(f"Maiores pedidos · {cat}")
    st.dataframe(
        df[df["categoria"] == cat]
        .nlargest(10, "receita")[["data", "produto", "regiao", "canal", "receita"]],
        use_container_width=True, hide_index=True,
        column_config={
            "data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
            "receita": st.column_config.NumberColumn("Receita", format="R$ %.2f"),
        },
    )
else:
    st.info("👆 Clique em uma barra para ver os maiores pedidos da categoria.")

st.divider()

# ==========================================================================
st.header("4 · Mapa, grafo e imagem")

m1, m2, m3 = st.tabs(["🗺️ st.map", "🔗 st.graphviz_chart", "🖼️ st.image"])

with m1:
    # Coordenadas aproximadas das capitais de cada região
    capitais = pd.DataFrame({
        "regiao": ["Nordeste", "Sudeste", "Sul", "Centro-Oeste", "Norte"],
        "lat": [-8.05, -23.55, -30.03, -15.79, -3.12],
        "lon": [-34.90, -46.63, -51.23, -47.88, -60.02],
    })
    receita_regiao = df.groupby("regiao", as_index=False)["receita"].sum()
    mapa = capitais.merge(receita_regiao, on="regiao")
    mapa["tamanho"] = mapa["receita"] / mapa["receita"].max() * 180_000

    st.map(mapa, latitude="lat", longitude="lon", size="tamanho", color="#ff4b4b")
    st.caption("`st.map` desenha pontos sobre um mapa base a partir de lat/lon.")

with m2:
    st.graphviz_chart("""
    digraph {
        rankdir=LR;
        node [shape=box, style="rounded,filled", fillcolor="#fff1f1",
              color="#ff4b4b", fontname="Helvetica"];
        CSV -> "Limpeza (AED)" -> "Agregação" -> "Figura Plotly" -> "st.plotly_chart";
        "Widgets" -> "Agregação" [style=dashed, label="filtro"];
    }
    """)
    st.caption("`st.graphviz_chart` aceita a linguagem DOT — ótimo para pipelines.")

with m3:
    # Gera uma imagem em memória para demonstrar st.image sem arquivo externo
    fig_img, ax = plt.subplots(figsize=(6, 2.2))
    mensal = df.groupby(pd.Grouper(key="data", freq="MS"))["receita"].sum()
    ax.fill_between(mensal.index, mensal.values, color="#ff4b4b", alpha=0.35)
    ax.plot(mensal.index, mensal.values, color="#c53030", linewidth=2)
    ax.set_axis_off()
    fig_img.tight_layout(pad=0)

    buffer = io.BytesIO()
    fig_img.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig_img)

    st.image(buffer.getvalue(), caption="Imagem PNG gerada em memória",
             use_container_width=True)
    st.code(
        '''from PIL import Image

back_img = Image.open("data/back_churn.png")
st.image(back_img, use_container_width=True)

# Arrays do OpenCV vêm em BGR:
st.image(array_cv2, channels="BGR")''',
        language="python")

    # Um array NumPy também é aceito diretamente
    gradiente = np.linspace(0, 255, 256, dtype=np.uint8)
    faixa = np.tile(gradiente, (40, 1))
    st.image(faixa, caption="Array NumPy exibido diretamente",
             use_container_width=True, clamp=True)
