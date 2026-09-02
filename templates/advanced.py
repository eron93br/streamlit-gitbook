"""Template AVANÇADO de dashboard Streamlit — multipágina, em um arquivo.

Ponto de partida para projetos com mais de um público ou que vão crescer.
Traz: navegação por páginas, cache com TTL, filtros persistentes entre
páginas, controle de perfil, estado vazio tratado, download e metodologia.

Este arquivo mantém tudo junto para você poder rodá-lo direto. Ao migrar
para um projeto real, distribua assim:

    meu-dashboard/
    ├── app.py            ← st.navigation, st.logo, set_page_config
    ├── dados.py          ← carregar(), agregar_*()
    ├── graficos.py       ← g_evolucao(), g_categoria(), ...
    ├── filtros.py        ← filtros_sidebar()
    └── views/
        ├── visao_geral.py
        ├── regioes.py
        ├── produtos.py
        └── dados_brutos.py

Uso:
    cp templates/advanced.py meu_projeto/app.py
    streamlit run app.py
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ==========================================================================
# CONFIGURAÇÃO
# ==========================================================================
st.set_page_config(
    page_title="Dashboard Corporativo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

CAMINHO_DADOS = Path(__file__).resolve().parents[1] / "data" / "vendas.csv"

CORES = px.colors.qualitative.Safe
LAYOUT = dict(margin=dict(t=50, b=0, l=0, r=0), height=380,
              legend=dict(orientation="h", y=-0.2, title=""))


# ==========================================================================
# CAMADA DE DADOS  (→ dados.py)
# ==========================================================================
@st.cache_data(ttl="30m", show_spinner="Carregando dados…")
def carregar(caminho: Path) -> pd.DataFrame:
    """TTL de 30 min: os dados são recarregados da origem periodicamente."""
    df = pd.read_csv(caminho, parse_dates=["data"])
    df["ano"] = df["data"].dt.year
    df["mes"] = df["data"].dt.to_period("M").dt.to_timestamp()
    df["margem"] = df["lucro"] / df["receita"]
    return df


@st.cache_data
def agregar_mensal(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("mes", as_index=False).agg(
        receita=("receita", "sum"), lucro=("lucro", "sum"),
        unidades=("unidades", "sum"), pedidos=("receita", "size"))


@st.cache_data
def agregar_por(df: pd.DataFrame, coluna: str) -> pd.DataFrame:
    return (
        df.groupby(coluna, as_index=False)
          .agg(receita=("receita", "sum"), lucro=("lucro", "sum"),
               unidades=("unidades", "sum"), pedidos=("receita", "size"))
          .sort_values("receita", ascending=False)
    )


def kpis(dados: pd.DataFrame) -> dict:
    receita = dados["receita"].sum()
    lucro = dados["lucro"].sum()
    return {
        "receita": receita,
        "lucro": lucro,
        "margem": lucro / receita if receita else 0.0,
        "ticket": receita / len(dados) if len(dados) else 0.0,
        "custo": dados["custo"].sum(),
    }


# ==========================================================================
# CAMADA DE GRÁFICOS  (→ graficos.py)
# ==========================================================================
def g_evolucao(mensal: pd.DataFrame):
    fig = px.line(mensal, x="mes", y=["receita", "lucro"], markers=True,
                  color_discrete_sequence=CORES,
                  labels={"mes": "", "value": "R$", "variable": ""},
                  title="Evolução mensal")
    fig.update_layout(hovermode="x unified", **LAYOUT)
    return fig


def g_barras(df: pd.DataFrame, coluna: str, titulo: str):
    dados = agregar_por(df, coluna)
    fig = px.bar(dados, x="receita", y=coluna, orientation="h",
                 color_discrete_sequence=CORES,
                 labels={"receita": "Receita (R$)", coluna: ""}, title=titulo)
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, **LAYOUT)
    return fig


def g_dispersao(df: pd.DataFrame):
    dados = df.groupby(["produto", "categoria"], as_index=False).agg(
        receita=("receita", "sum"), unidades=("unidades", "sum"),
        margem=("margem", "mean"))
    fig = px.scatter(dados, x="unidades", y="receita", size="margem",
                     color="categoria", hover_name="produto",
                     color_discrete_sequence=CORES,
                     labels={"unidades": "Unidades", "receita": "Receita (R$)"},
                     title="Volume × receita por produto")
    fig.update_layout(**LAYOUT)
    return fig


def g_calor(df: pd.DataFrame):
    tabela = df.pivot_table(index="regiao", columns="categoria",
                            values="receita", aggfunc="sum")
    fig = px.imshow(tabela, text_auto=".2s", aspect="auto",
                    color_continuous_scale="Reds",
                    labels=dict(color="Receita"),
                    title="Receita por região e categoria")
    fig.update_layout(coloraxis_showscale=False, **LAYOUT)
    return fig


# ==========================================================================
# FILTROS COMPARTILHADOS  (→ filtros.py)
# ==========================================================================
def filtros_sidebar(df: pd.DataFrame) -> pd.DataFrame:
    """Desenha os filtros e devolve o DataFrame filtrado.

    Os `key` fazem as escolhas persistirem na troca de página.
    """
    def limpar():
        st.session_state.f_regiao = sorted(df["regiao"].unique())
        st.session_state.f_categoria = sorted(df["categoria"].unique())
        st.session_state.f_canal = sorted(df["canal"].unique())

    with st.sidebar:
        st.header("Filtros")
        st.button("↺ Limpar", on_click=limpar, use_container_width=True)

        regioes = st.multiselect(
            "Região", sorted(df["regiao"].unique()),
            default=sorted(df["regiao"].unique()), key="f_regiao")
        categorias = st.multiselect(
            "Categoria", sorted(df["categoria"].unique()),
            default=sorted(df["categoria"].unique()), key="f_categoria")
        canais = st.multiselect(
            "Canal", sorted(df["canal"].unique()),
            default=sorted(df["canal"].unique()), key="f_canal")

        d_min, d_max = df["data"].min().date(), df["data"].max().date()
        periodo = st.date_input("Período", value=(d_min, d_max),
                                min_value=d_min, max_value=d_max, key="f_periodo")

        st.divider()
        if st.button("🔄 Atualizar dados", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    mask = (
        df["regiao"].isin(regioes)
        & df["categoria"].isin(categorias)
        & df["canal"].isin(canais)
    )
    if isinstance(periodo, (tuple, list)) and len(periodo) == 2:
        mask &= df["data"].between(pd.Timestamp(periodo[0]),
                                   pd.Timestamp(periodo[1]))

    filtrado = df[mask]
    if filtrado.empty:
        st.warning("Nenhum registro corresponde aos filtros. Amplie a seleção.")
        st.stop()

    st.sidebar.caption(
        f"{len(filtrado):,} de {len(df):,} registros "
        f"({len(filtrado) / len(df):.0%})"
    )
    return filtrado


def linha_kpis(df: pd.DataFrame, mostrar_financeiro: bool) -> None:
    """KPIs sensíveis (custo, margem) só aparecem para perfis autorizados."""
    ultimo = int(df["ano"].max())
    atual, anterior = (
        kpis(df[df["ano"] == ultimo]),
        kpis(df[df["ano"] == ultimo - 1]),
    )

    def delta(chave):
        if not anterior[chave]:
            return None
        return f"{atual[chave] / anterior[chave] - 1:+.1%}"

    n = 5 if mostrar_financeiro else 3
    cols = st.columns(n)
    cols[0].metric("Receita", f"R$ {atual['receita']:,.0f}",
                   delta("receita"), border=True)
    cols[1].metric("Pedidos", f"{len(df[df['ano'] == ultimo]):,}", border=True)
    cols[2].metric("Ticket médio", f"R$ {atual['ticket']:,.0f}",
                   delta("ticket"), border=True)

    if mostrar_financeiro:
        cols[3].metric(
            "Margem", f"{atual['margem']:.1%}",
            f"{(atual['margem'] - anterior['margem']) * 100:+.1f} p.p."
            if anterior["margem"] else None, border=True)
        cols[4].metric("Custo", f"R$ {atual['custo']:,.0f}", delta("custo"),
                       delta_color="inverse", border=True)

    st.caption(f"Comparação {ultimo} vs. {ultimo - 1}.")


# ==========================================================================
# PÁGINAS  (→ views/*.py)
# ==========================================================================
def pagina_visao_geral():
    df = filtros_sidebar(carregar(CAMINHO_DADOS))
    financeiro = st.session_state.get("perfil") in ("Diretoria", "Financeiro")

    st.title("📊 Visão geral")
    st.caption(f"{df['data'].min():%d/%m/%Y} a {df['data'].max():%d/%m/%Y}")

    linha_kpis(df, financeiro)
    st.divider()

    esq, dir_ = st.columns([3, 2], gap="large")
    esq.plotly_chart(g_evolucao(agregar_mensal(df)), use_container_width=True)
    dir_.plotly_chart(g_barras(df, "categoria", "Receita por categoria"),
                      use_container_width=True)

    if not financeiro:
        st.info(
            "🔒 Margem e custo estão disponíveis apenas para os perfis "
            "Diretoria e Financeiro. Troque o perfil na barra lateral para ver."
        )


def pagina_regioes():
    df = filtros_sidebar(carregar(CAMINHO_DADOS))

    st.title("🗺️ Regiões")
    esq, dir_ = st.columns(2, gap="large")
    esq.plotly_chart(g_barras(df, "regiao", "Receita por região"),
                     use_container_width=True)
    dir_.plotly_chart(g_calor(df), use_container_width=True)

    st.dataframe(
        agregar_por(df, "regiao"), use_container_width=True, hide_index=True,
        column_config={
            "regiao": "Região",
            "receita": st.column_config.NumberColumn("Receita", format="R$ %.0f"),
            "lucro": st.column_config.NumberColumn("Lucro", format="R$ %.0f"),
            "unidades": st.column_config.NumberColumn("Unidades", format="%d"),
            "pedidos": st.column_config.NumberColumn("Pedidos", format="%d"),
        },
    )


def pagina_produtos():
    df = filtros_sidebar(carregar(CAMINHO_DADOS))

    st.title("🧴 Produtos")
    st.plotly_chart(g_dispersao(df), use_container_width=True)

    detalhe = (
        df.groupby(["categoria", "produto"], as_index=False)
        .agg(receita=("receita", "sum"), lucro=("lucro", "sum"),
             unidades=("unidades", "sum"), satisfacao=("satisfacao", "mean"))
        .sort_values("receita", ascending=False)
    )
    detalhe["margem_pct"] = (detalhe["lucro"] / detalhe["receita"] * 100).round(1)

    st.dataframe(
        detalhe, use_container_width=True, hide_index=True,
        column_config={
            "categoria": "Categoria",
            "produto": "Produto",
            "receita": st.column_config.NumberColumn("Receita", format="R$ %.0f"),
            "lucro": st.column_config.NumberColumn("Lucro", format="R$ %.0f"),
            "unidades": st.column_config.NumberColumn("Unid.", format="%d"),
            "margem_pct": st.column_config.ProgressColumn(
                "Margem", format="%.1f%%", min_value=0, max_value=60),
            "satisfacao": st.column_config.NumberColumn("Satisf.", format="%.1f ⭐"),
        },
    )


def pagina_dados():
    df = filtros_sidebar(carregar(CAMINHO_DADOS))

    st.title("📋 Dados brutos")
    n = st.slider("Linhas a exibir", 50, 2000, 300, step=50)
    st.dataframe(df.head(n), use_container_width=True, hide_index=True, height=440)

    st.download_button(
        "⬇️ Baixar recorte (CSV)",
        df.to_csv(index=False).encode("utf-8-sig"),
        file_name="recorte.csv", mime="text/csv",
    )
    st.caption(
        "⚠️ O download é uma porta de saída de dados. Em ambiente corporativo, "
        "avalie restringi-lo por perfil."
    )


def pagina_metodologia():
    st.title("📖 Metodologia")
    st.markdown(
        """
### Definições

| Métrica | Fórmula | Dono |
| --- | --- | --- |
| Receita | Σ (unidades × preço unitário) | Comercial |
| Lucro | receita − custo direto | Financeiro |
| Margem | lucro / receita (em p.p.) | Financeiro |
| Ticket médio | receita / nº de pedidos | Comercial |

### Tratamento de dados

- `satisfacao` possui ~1,5% de valores ausentes, ignorados no cálculo da média.
- Não há duplicatas; a cobertura temporal é completa no período.
- Custos indiretos **não** estão incluídos no lucro.

### Atualização

Os dados são cacheados por 30 minutos (`ttl="30m"`). Use **Atualizar dados** na
barra lateral para forçar uma releitura.
"""
    )


# ==========================================================================
# ENTRADA DO APP  (→ app.py)
# ==========================================================================
if not CAMINHO_DADOS.exists():
    st.error(f"Dataset não encontrado em `{CAMINHO_DADOS}`.")
    st.stop()

# Perfil do usuário — em produção, viria de um sistema de autenticação
# (st.user, streamlit-authenticator, ou um proxy com SSO), NUNCA de um widget.
with st.sidebar:
    st.selectbox("Perfil (simulado)",
                 ["Comercial", "Financeiro", "Diretoria"], key="perfil")

pg_visao = st.Page(pagina_visao_geral, title="Visão geral",
                   icon=":material/dashboard:", default=True)
pg_regioes = st.Page(pagina_regioes, title="Regiões", icon=":material/map:")
pg_produtos = st.Page(pagina_produtos, title="Produtos",
                      icon=":material/inventory_2:")
pg_dados = st.Page(pagina_dados, title="Dados brutos", icon=":material/table:")
pg_metodo = st.Page(pagina_metodologia, title="Metodologia",
                    icon=":material/info:")

# Menu montado condicionalmente — páginas sensíveis só para perfis autorizados
paginas = {"Análise": [pg_visao, pg_regioes, pg_produtos]}
if st.session_state.get("perfil") in ("Diretoria", "Financeiro"):
    paginas["Apoio"] = [pg_dados, pg_metodo]
else:
    paginas["Apoio"] = [pg_metodo]

st.navigation(paginas).run()
