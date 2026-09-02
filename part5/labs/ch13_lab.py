"""Laboratório 13 — App multipágina com st.navigation, em um arquivo só.

`st.Page` aceita uma **função** além de um caminho de arquivo. Isso permite
demonstrar navegação multipágina sem criar a estrutura de pastas — útil para
estudar, mas em um projeto real prefira um arquivo por página (`views/`).

Execute na raiz do repositório:
    streamlit run part5/labs/ch13_lab.py
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Lab 13 · Multipágina", page_icon="🧭",
                   layout="wide", initial_sidebar_state="expanded")

RAIZ = Path(__file__).resolve().parents[2]
CSV = RAIZ / "data" / "vendas.csv"

LAYOUT = dict(height=360, margin=dict(t=40, b=0, l=0, r=0),
              legend=dict(orientation="h", y=-0.2, title=""))


# ==========================================================================
# Módulo de dados compartilhado — a melhor forma de dividir dados entre páginas
# ==========================================================================
@st.cache_data(show_spinner="Carregando dados…")
def carregar() -> pd.DataFrame:
    df = pd.read_csv(CSV, parse_dates=["data"])
    df["mes"] = df["data"].dt.to_period("M").dt.to_timestamp()
    return df


def filtros_comuns(df: pd.DataFrame) -> pd.DataFrame:
    """Filtros na sidebar, com `key` para persistirem na troca de página."""
    with st.sidebar:
        st.subheader("Filtros")
        regioes = st.multiselect(
            "Região", sorted(df["regiao"].unique()),
            default=st.session_state.get("filtro_regiao",
                                         sorted(df["regiao"].unique())),
            key="filtro_regiao",
        )
        canais = st.multiselect(
            "Canal", sorted(df["canal"].unique()),
            default=st.session_state.get("filtro_canal",
                                         sorted(df["canal"].unique())),
            key="filtro_canal",
        )
    sub = df[df["regiao"].isin(regioes) & df["canal"].isin(canais)]
    if sub.empty:
        st.warning("Nenhum registro para os filtros. Amplie a seleção.")
        st.stop()
    st.sidebar.caption(f"{len(sub):,} de {len(df):,} registros")
    return sub


# ==========================================================================
# As páginas
# ==========================================================================
def pagina_visao_geral():
    df = filtros_comuns(carregar())

    st.title("📊 Visão geral")
    st.caption(f"{df['data'].min():%d/%m/%Y} a {df['data'].max():%d/%m/%Y}")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Receita", f"R$ {df['receita'].sum():,.0f}", border=True)
    k2.metric("Lucro", f"R$ {df['lucro'].sum():,.0f}", border=True)
    k3.metric("Margem", f"{df['lucro'].sum() / df['receita'].sum():.1%}", border=True)
    k4.metric("Pedidos", f"{len(df):,}", border=True)

    mensal = df.groupby("mes", as_index=False)[["receita", "lucro"]].sum()
    fig = px.line(mensal, x="mes", y=["receita", "lucro"], markers=True,
                  labels={"mes": "", "value": "R$", "variable": ""},
                  title="Evolução mensal")
    fig.update_layout(hovermode="x unified", **LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Navegação programática")
    c1, c2 = st.columns(2)
    with c1:
        st.caption("`st.page_link` — desenha um link:")
        st.page_link("https://docs.streamlit.io/develop/api-reference/navigation",
                     label="Documentação de navegação", icon="🔗")
    with c2:
        st.caption("`st.switch_page` — navega ao clicar:")
        if st.button("Ir para Regiões →"):
            st.switch_page(pg_regioes)


def pagina_regioes():
    df = filtros_comuns(carregar())

    st.title("🗺️ Regiões")
    st.caption("Os filtros da sidebar persistiram na troca de página.")

    por_regiao = (
        df.groupby("regiao", as_index=False)
          .agg(receita=("receita", "sum"), lucro=("lucro", "sum"),
               pedidos=("receita", "size"))
          .sort_values("receita", ascending=False)
    )

    esq, dir_ = st.columns([3, 2], gap="large")

    fig = px.bar(por_regiao, x="receita", y="regiao", orientation="h",
                 labels={"receita": "Receita (R$)", "regiao": ""},
                 title="Receita por região")
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, **LAYOUT)
    esq.plotly_chart(fig, use_container_width=True)

    tabela = df.pivot_table(index="regiao", columns="categoria",
                            values="receita", aggfunc="sum")
    fig2 = px.imshow(tabela, text_auto=".2s", aspect="auto",
                     color_continuous_scale="Reds",
                     title="Região × categoria")
    fig2.update_layout(coloraxis_showscale=False, **LAYOUT)
    dir_.plotly_chart(fig2, use_container_width=True)

    st.dataframe(
        por_regiao, use_container_width=True, hide_index=True,
        column_config={
            "regiao": "Região",
            "receita": st.column_config.NumberColumn("Receita", format="R$ %.0f"),
            "lucro": st.column_config.NumberColumn("Lucro", format="R$ %.0f"),
            "pedidos": st.column_config.NumberColumn("Pedidos", format="%d"),
        },
    )


def pagina_dados():
    df = filtros_comuns(carregar())

    st.title("📋 Dados brutos")
    n = st.slider("Linhas a exibir", 50, 2000, 300, step=50)

    st.dataframe(
        df.head(n), use_container_width=True, hide_index=True, height=460,
        column_config={
            "data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
            "receita": st.column_config.NumberColumn("Receita", format="R$ %.2f"),
            "lucro": st.column_config.NumberColumn("Lucro", format="R$ %.2f"),
        },
    )

    st.download_button(
        "⬇️ Baixar recorte completo (CSV)",
        df.to_csv(index=False).encode("utf-8-sig"),
        file_name="recorte_vendas.csv",
        mime="text/csv",
    )


def pagina_sobre():
    st.title("ℹ️ Sobre este app")
    st.markdown(
        """
Este laboratório demonstra `st.navigation` + `st.Page` usando **funções** em vez
de arquivos, para caber em um único script.

### Em um projeto real, prefira:

```text
meu-dashboard/
├── app.py              ← st.navigation, st.logo, set_page_config
├── dados.py            ← carga cacheada, compartilhada
├── graficos.py         ← uma função por figura
└── views/
    ├── visao_geral.py
    ├── regioes.py
    └── dados_brutos.py
```

```python
pg = st.navigation({
    "Análise": [
        st.Page("views/visao_geral.py", title="Visão geral",
                icon=":material/dashboard:", default=True),
        st.Page("views/regioes.py", title="Regiões", icon=":material/map:"),
    ],
    "Apoio": [
        st.Page("views/dados_brutos.py", title="Dados", icon=":material/table:"),
    ],
})
pg.run()
```

### Páginas condicionais

Como a estrutura é montada em Python, ela pode depender de qualquer condição:

```python
paginas = {"Análise": [visao_geral, regioes]}
if st.session_state.get("perfil") == "diretoria":
    paginas["Financeiro"] = [margem, custos]
pg = st.navigation(paginas)
```

⚠️ **Esconder uma página do menu não é controle de acesso.** A verificação
precisa existir dentro da própria página, antes do carregamento do dado
sensível.
"""
    )
    with st.expander("🔍 Estado compartilhado entre páginas"):
        st.json({k: str(v)[:120] for k, v in st.session_state.items()})


# ==========================================================================
# Registro das páginas e execução
# ==========================================================================
if not CSV.exists():
    st.error("Rode `python scripts/gerar_dados.py` na raiz do repositório.")
    st.stop()

pg_visao = st.Page(pagina_visao_geral, title="Visão geral",
                   icon=":material/dashboard:", default=True, url_path="visao-geral")
pg_regioes = st.Page(pagina_regioes, title="Regiões",
                     icon=":material/map:", url_path="regioes")
pg_dados = st.Page(pagina_dados, title="Dados brutos",
                   icon=":material/table:", url_path="dados")
pg_sobre = st.Page(pagina_sobre, title="Sobre",
                   icon=":material/info:", url_path="sobre")

navegacao = st.navigation(
    {
        "Análise": [pg_visao, pg_regioes],
        "Apoio": [pg_dados, pg_sobre],
    }
)

navegacao.run()
