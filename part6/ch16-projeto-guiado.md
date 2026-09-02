---
title: "16. Projeto guiado: dashboard de vendas"
subject: "Parte 6: Construindo o Dashboard"
---

# Projeto guiado: dashboard de vendas

:::{admonition} O que você vai aprender
:class: tip
- Construir, do zero ao app publicável, um dashboard completo em seis etapas
- Organizar o projeto em módulos: `dados.py`, `graficos.py`, `app.py`
- Combinar tudo o que veio antes: cache, filtros, KPIs, layout, abas e download
- Um checklist final antes de entregar
:::

:::{div}
:class: run-quick
**Rode este código:** [`part6/labs/ch16_lab.py`](./labs/ch16_lab.py) — o
dashboard completo, em um arquivo único, pronto para rodar.
`streamlit run part6/labs/ch16_lab.py`
:::

## Visão geral

Este capítulo põe em prática a ficha preenchida no
[Capítulo 15](./ch15-roteiro-de-dashboard.md):

```text
Nome:     Dashboard de Vendas 2024–2025
Tipo:     Analítico
Público:  Gerência comercial
Decisão:  Onde realocar o esforço comercial no próximo trimestre
KPIs:     Receita · Lucro · Margem · Ticket médio
Gráficos: evolução mensal · categoria×canal · produtos · região×categoria
```

A construção segue seis etapas, cada uma acrescentando uma camada:

| Etapa | O que entra | Capítulo de origem |
| --- | --- | --- |
| 1 | Estrutura e configuração da página | 3 |
| 2 | Carga de dados com cache | 11 |
| 3 | Filtros na sidebar | 9 |
| 4 | Linha de KPIs | 7 |
| 5 | Gráficos em grade e abas | 6, 8, 12 |
| 6 | Detalhamento, download e acabamento | 5, 7 |

## Mãos à obra

### Etapa 1 · Estrutura do projeto

```text
dashboard-vendas/
├── app.py
├── dados.py
├── graficos.py
├── data/
│   └── vendas.csv
├── .streamlit/
│   └── config.toml
└── requirements.txt
```

```toml
# .streamlit/config.toml
[theme]
base = "light"
primaryColor = "#FF4B4B"
secondaryBackgroundColor = "#F4F6F9"

[browser]
gatherUsageStats = false
```

```python
# app.py — etapa 1
import streamlit as st

st.set_page_config(
    page_title="Dashboard de Vendas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📊 Dashboard de Vendas")
st.caption("Análise comercial 2024–2025 · dados sintéticos")
```

### Etapa 2 · Carga de dados com cache

```python
# dados.py
from pathlib import Path

import pandas as pd
import streamlit as st

CAMINHO = Path(__file__).parent / "data" / "vendas.csv"


@st.cache_data(show_spinner="Carregando dados…")
def carregar() -> pd.DataFrame:
    """Lê o CSV, converte tipos e deriva colunas de apoio."""
    df = pd.read_csv(CAMINHO, parse_dates=["data"])
    df["ano"] = df["data"].dt.year
    df["mes"] = df["data"].dt.to_period("M").dt.to_timestamp()
    df["margem"] = df["lucro"] / df["receita"]
    return df


@st.cache_data
def agregar_mensal(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("mes", as_index=False).agg(
        receita=("receita", "sum"),
        lucro=("lucro", "sum"),
        unidades=("unidades", "sum"),
        pedidos=("receita", "size"),
    )
```

```python
# app.py — etapa 2 (continuação)
from dados import carregar

try:
    df = carregar()
except FileNotFoundError:
    st.error("Dataset não encontrado. Rode `python scripts/gerar_dados.py`.")
    st.stop()
```

:::{admonition} Por que a coluna `mes` é derivada na carga
:class: tip
Porque a derivação entra no cache. Fazê-la depois do filtro significaria
recalculá-la a cada interação.
:::

### Etapa 3 · Filtros na sidebar

```python
# app.py — etapa 3
import pandas as pd

with st.sidebar:
    st.header("Filtros")

    regioes = st.multiselect(
        "Região", sorted(df["regiao"].unique()),
        default=sorted(df["regiao"].unique()),
    )
    categorias = st.multiselect(
        "Categoria", sorted(df["categoria"].unique()),
        default=sorted(df["categoria"].unique()),
    )
    canais = st.multiselect(
        "Canal", sorted(df["canal"].unique()),
        default=sorted(df["canal"].unique()),
    )

    d_min, d_max = df["data"].min().date(), df["data"].max().date()
    periodo = st.date_input("Período", value=(d_min, d_max),
                            min_value=d_min, max_value=d_max)

    st.divider()
    if st.button("↺ Limpar cache e recarregar", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.caption("Dados sintéticos · `scripts/gerar_dados.py`")


def aplicar_filtros(df, regioes, categorias, canais, periodo):
    mask = (
        df["regiao"].isin(regioes)
        & df["categoria"].isin(categorias)
        & df["canal"].isin(canais)
    )
    if isinstance(periodo, (tuple, list)) and len(periodo) == 2:
        inicio, fim = periodo
        mask &= df["data"].between(pd.Timestamp(inicio), pd.Timestamp(fim))
    return df[mask]


filtrado = aplicar_filtros(df, regioes, categorias, canais, periodo)

if filtrado.empty:
    st.warning("Nenhum registro corresponde aos filtros. Amplie a seleção.")
    st.stop()
```

### Etapa 4 · A linha de KPIs

```python
# app.py — etapa 4
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


ultimo_ano = filtrado["ano"].max()
atual = kpis(filtrado[filtrado["ano"] == ultimo_ano])
anterior = kpis(filtrado[filtrado["ano"] == ultimo_ano - 1])


def delta(chave, formato="{:+.1%}"):
    if not anterior[chave]:
        return None
    return formato.format(atual[chave] / anterior[chave] - 1)


st.subheader(f"Indicadores · {ultimo_ano}")
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Receita", f"R$ {atual['receita']:,.0f}", delta("receita"), border=True)
k2.metric("Lucro", f"R$ {atual['lucro']:,.0f}", delta("lucro"), border=True)
k3.metric("Margem", f"{atual['margem']:.1%}",
          f"{(atual['margem'] - anterior['margem']) * 100:+.1f} p.p."
          if anterior["margem"] else None, border=True)
k4.metric("Ticket médio", f"R$ {atual['ticket']:,.0f}", delta("ticket"), border=True)
k5.metric("Custo", f"R$ {atual['custo']:,.0f}", delta("custo"),
          delta_color="inverse", border=True)   # subir custo é ruim
```

:::{admonition} Margem em pontos percentuais
:class: warning
A variação de uma métrica que já é percentual deve ser expressa em **pontos
percentuais** (p.p.), não em porcentagem. Ir de 30% para 33% é +3 p.p. (ou
+10%) — dizer "+10%" para uma margem confunde quase todo mundo.
:::

### Etapa 5 · Gráficos

```python
# graficos.py
import pandas as pd
import plotly.express as px

CORES = px.colors.qualitative.Safe
LAYOUT = dict(margin=dict(t=40, b=0, l=0, r=0), height=380,
              legend=dict(orientation="h", y=-0.18, title=""))


def evolucao(mensal: pd.DataFrame):
    fig = px.line(mensal, x="mes", y=["receita", "lucro"], markers=True,
                  color_discrete_sequence=CORES,
                  labels={"mes": "", "value": "R$", "variable": ""},
                  title="Evolução mensal")
    fig.update_layout(hovermode="x unified", **LAYOUT)
    return fig


def por_categoria(df: pd.DataFrame):
    dados = df.groupby(["categoria", "canal"], as_index=False)["receita"].sum()
    fig = px.bar(dados, x="receita", y="categoria", color="canal",
                 orientation="h", barmode="group",
                 color_discrete_sequence=CORES,
                 labels={"receita": "Receita (R$)", "categoria": "", "canal": ""},
                 title="Receita por categoria e canal")
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, **LAYOUT)
    return fig


def produtos(df: pd.DataFrame):
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


def mapa_calor(df: pd.DataFrame):
    tabela = df.pivot_table(index="regiao", columns="categoria",
                            values="receita", aggfunc="sum")
    fig = px.imshow(tabela, text_auto=".2s", aspect="auto",
                    color_continuous_scale="Reds",
                    labels=dict(color="Receita"),
                    title="Receita por região e categoria")
    fig.update_layout(**LAYOUT, coloraxis_showscale=False)
    return fig
```

```python
# app.py — etapa 5
from dados import agregar_mensal
from graficos import evolucao, por_categoria, produtos, mapa_calor

st.divider()

esq, dir_ = st.columns([3, 2], gap="large")
with esq:
    st.plotly_chart(evolucao(agregar_mensal(filtrado)), use_container_width=True)
with dir_:
    st.plotly_chart(por_categoria(filtrado), use_container_width=True)

aba_prod, aba_reg = st.tabs(["🧴 Produtos", "🗺️ Região × Categoria"])
with aba_prod:
    st.plotly_chart(produtos(filtrado), use_container_width=True)
with aba_reg:
    st.plotly_chart(mapa_calor(filtrado), use_container_width=True)
```

### Etapa 6 · Detalhamento, download e acabamento

```python
# app.py — etapa 6
st.divider()

with st.expander("📋 Detalhamento por produto", expanded=False):
    detalhe = (
        filtrado.groupby(["categoria", "produto"], as_index=False)
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

    st.download_button(
        "⬇️ Baixar detalhamento (CSV)",
        detalhe.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"detalhamento_{ultimo_ano}.csv",
        mime="text/csv",
    )

with st.expander("📖 Metodologia"):
    st.markdown("""
    - **Receita** — soma de `unidades × preço unitário`.
    - **Lucro** — receita menos custo direto; não inclui despesas indiretas.
    - **Margem** — lucro dividido pela receita, em pontos percentuais.
    - **Ticket médio** — receita dividida pelo número de pedidos.
    - **Satisfação** — média das notas de 1 a 5; ~1,5% dos registros são nulos e
      são ignorados no cálculo.
    """)
    st.caption("Fonte: dados sintéticos gerados por `scripts/gerar_dados.py`.")

st.caption(
    f"{len(filtrado):,} de {len(df):,} registros exibidos "
    f"({len(filtrado) / len(df):.0%}) · última atualização: "
    f"{df['data'].max():%d/%m/%Y}"
)
```

## Checklist final

- [ ] `st.set_page_config` é o primeiro comando, com `layout="wide"`
- [ ] Toda carga e agregação cara está sob `@st.cache_data`
- [ ] O caso de filtro vazio é tratado com `st.warning` + `st.stop`
- [ ] Todo KPI tem unidade, período e comparação
- [ ] Métricas em que "subir é ruim" usam `delta_color="inverse"`
- [ ] Variação de percentual está em pontos percentuais
- [ ] Barras estão ordenadas por valor
- [ ] Figuras têm `use_container_width=True` e margens ajustadas
- [ ] Há metodologia documentada no próprio app
- [ ] Há data de atualização visível
- [ ] Existe caminho de download do recorte
- [ ] `requirements.txt` está atualizado para o deploy

:::{card} **Vá além**
O laboratório [`ch16_lab.py`](./labs/ch16_lab.py) é este dashboard em um arquivo
único, comentado etapa por etapa. Os templates
[`basic.py`](../part7/ch18-templates-e-galeria.md) e `advanced.py` trazem o mesmo
código organizado como ponto de partida para o seu próprio projeto.
:::

## Questões para reflexão

1. O projeto separa `dados.py`, `graficos.py` e `app.py`. Que outra separação
   você faria se o dashboard crescesse para cinco páginas?
2. A função `kpis()` recebe um DataFrame e devolve um dicionário. Que vantagem de
   teste isso oferece sobre calcular os KPIs inline no `app.py`?
3. O dashboard compara o último ano com o anterior. Que outras bases de
   comparação fariam sentido, e como a escolha muda a leitura?
4. A metodologia está em um expander fechado. Que argumento existe para deixá-la
   sempre visível?
5. O download exporta o recorte filtrado. Que informação de contexto deveria
   acompanhar o CSV para que ele não seja mal interpretado fora do dashboard?

## Teste você mesmo

:::{dropdown} **Q1.** Por que derivar as colunas `mes` e `margem` dentro da função cacheada de carga?
**Resposta:** porque assim a derivação entra no cache e acontece uma única vez.
Se fosse feita depois da filtragem, seria recalculada a cada interação do
usuário.
:::

:::{dropdown} **Q2.** Como o dashboard trata o caso em que os filtros não retornam nenhuma linha?
**Resposta:** exibe `st.warning` com orientação para ampliar a seleção e chama
`st.stop()`, encerrando o rerun antes de tentar desenhar KPIs e gráficos sobre um
DataFrame vazio.
:::

:::{dropdown} **Q3.** Por que o KPI de custo usa `delta_color="inverse"`?
**Resposta:** porque o Streamlit assume que um delta positivo é bom e o pinta de
verde. Para custo, um aumento é ruim — `inverse` troca as cores e comunica o
sentido correto.
:::

:::{dropdown} **Q4.** Como se expressa corretamente a variação de uma margem de 30% para 33%?
**Resposta:** como **+3 pontos percentuais (p.p.)**. Dizer "+10%" é tecnicamente
verdadeiro em termos relativos, mas confunde — em métricas que já são
percentuais, use p.p.
:::

:::{dropdown} **Q5.** Qual a vantagem de manter as figuras em `graficos.py`, com uma função por gráfico?
**Resposta:** as funções podem ser testadas isoladamente no notebook, reutilizadas
em várias páginas e ajustadas sem tocar no código de interface. O `app.py` fica
com uma linha por gráfico, muito mais legível e fácil de reorganizar.
:::

:::{dropdown} **Q6.** Que três informações de contexto todo dashboard deveria exibir na tela?
**Resposta:** o período coberto pelos dados, a data da última atualização e o
número de registros exibidos em relação ao total (o efeito dos filtros). Sem
isso, o usuário não sabe se está vendo tudo, nem quão atual é o número.
:::

---

:::{div}
:class: chapter-footer
[← Capítulo 15](./ch15-roteiro-de-dashboard.md) · [Índice](../conteudo.md) ·
[Capítulo 17 → Deploy](../part7/ch17-deploy.md)
:::
