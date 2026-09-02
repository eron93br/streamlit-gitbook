---
title: "6. Plotly Express: estruture antes de plugar"
subject: "Parte 3: Dados e Gráficos"
---

# Plotly Express: estruture antes de plugar

:::{admonition} O que você vai aprender
:class: tip
- Por que estruturar os gráficos **no notebook** antes de levá-los ao dashboard
- O modelo mental do Plotly Express: uma função, uma figura, um DataFrame *tidy*
- Os cinco gráficos que resolvem 90% de um dashboard analítico
- Como customizar cores, rótulos, hover e layout
- Como transformar o código do notebook em uma **função** reutilizável no app
:::

:::{div}
:class: run-quick
**Rode este código:** [`part3/labs/ch06_lab.py`](./labs/ch06_lab.py) — o app que
mostra as figuras finais. Mas comece pelo notebook: este é o único capítulo em
que a recomendação é **abrir o Colab primeiro**.
:::

:::{div}
:class: api-ref
🔗 **Referência:** [Plotly Express](https://plotly.com/python/plotly-express/)
· [Galeria de gráficos](https://plotly.com/python/)
· [`st.plotly_chart`](https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart)
:::

## Visão geral

### ⚠️ A regra mais importante deste livro

:::{admonition} Estruture os gráficos no notebook, depois leve para o app
:class: important
Imagine que seu dashboard terá quatro gráficos. **Faça os quatro no
Colab/Jupyter primeiro.** Só quando o código estiver produzindo exatamente a
figura desejada é que ele vai para o arquivo `.py` do dashboard.
:::

Por que isso importa tanto? Porque depurar um gráfico dentro de um app Streamlit
é lento e enganoso:

| No notebook | No app Streamlit |
| --- | --- |
| A célula roda em 1 segundo | O script inteiro reexecuta a cada salvamento |
| O erro aparece na célula, com contexto | O erro aparece no terminal, e a página fica em branco |
| Você inspeciona `df.head()` em qualquer ponto | Você precisa adicionar um `st.write(df)` e recarregar |
| Uma figura errada é uma figura errada | Uma figura errada pode ser um problema de layout, cache, filtro ou dado |

Quando o gráfico chega ao app já testado, qualquer problema restante é
**do app**, não da figura. Isso reduz drasticamente o espaço de busca.

### Por que Plotly Express

O módulo `plotly.express` (importado por convenção como `px`) constrói figuras
completas com uma única chamada. É a porta de entrada recomendada do Plotly e a
que melhor se integra a dashboards, porque as figuras resultantes são
**interativas nativamente**: zoom, pan, hover, legenda clicável e exportação em
PNG, sem nenhuma linha extra.

```python
import plotly.express as px

data_canada = px.data.gapminder().query("country == 'Canada'")
fig = px.bar(data_canada, x="year", y="pop")
fig.show()
```

Comparado a Matplotlib/Seaborn:

| | Plotly Express | Matplotlib / Seaborn |
| --- | --- | --- |
| Interatividade | Nativa (hover, zoom, legenda) | Nenhuma (imagem estática) |
| Integração com Streamlit | `st.plotly_chart(fig)` | `st.pyplot(fig)` |
| Publicação estática (PDF, slide) | Requer exportação | Excelente |
| Controle fino do desenho | Bom | Total |

**Em dashboards, prefira Plotly.** Matplotlib e Seaborn continuam ótimos para
relatórios em PDF e para gráficos estatísticos específicos (veja o
[Capítulo 8](./ch08-funcoes-graficas-e-midia.md)).

### O formato que o Plotly espera: *tidy data*

Quase todo erro de iniciante com `px` é um erro de formato dos dados. O Plotly
Express espera um DataFrame **longo (tidy)**: uma observação por linha, uma
variável por coluna.

```text
❌ formato largo                    ✅ formato longo (tidy)
regiao      2024     2025           regiao      ano   receita
Nordeste    1200     1450           Nordeste    2024     1200
Sudeste     2100     2380           Nordeste    2025     1450
                                    Sudeste     2024     2100
                                    Sudeste     2025     2380
```

A conversão é feita com `pandas.melt`:

```python
longo = largo.melt(id_vars="regiao", var_name="ano", value_name="receita")
```

Com os dados nesse formato, `px` mapeia colunas para propriedades visuais:
`x`, `y`, `color`, `size`, `facet_col`, `symbol`, `hover_data`.

### Os cinco gráficos que resolvem um dashboard

| Pergunta do usuário | Gráfico | Função |
| --- | --- | --- |
| Como evoluiu ao longo do tempo? | Linha | `px.line` |
| Quem é maior? | Barras | `px.bar` |
| Duas variáveis se relacionam? | Dispersão | `px.scatter` |
| Como se distribui? | Histograma / box | `px.histogram`, `px.box` |
| Onde estão os pontos quentes? | Mapa de calor | `px.imshow`, `px.density_heatmap` |

Acrescente `px.pie`/`px.sunburst` para composição (com moderação) e
`px.treemap` para hierarquias.

## Mãos à obra

Trabalhe as etapas 1 a 4 **no notebook**. A etapa 5 é a passagem para o app.

**Passo 1 — Carregar e conferir o formato.**

```python
import pandas as pd
import plotly.express as px

df = pd.read_csv("data/vendas.csv", parse_dates=["data"])
df.head()
df.dtypes
```

**Passo 2 — Série temporal (evolução).**

```python
mensal = (
    df.groupby(pd.Grouper(key="data", freq="MS"), as_index=False)
      .agg(receita=("receita", "sum"), lucro=("lucro", "sum"))
)

fig_linha = px.line(
    mensal,
    x="data",
    y=["receita", "lucro"],
    markers=True,
    labels={"data": "Mês", "value": "R$", "variable": "Métrica"},
    title="Receita e lucro por mês",
)
fig_linha.update_layout(hovermode="x unified", legend_title_text="")
fig_linha.show()
```

`hovermode="x unified"` é um detalhe pequeno com efeito grande: mostra todas as
séries no mesmo tooltip, permitindo comparação direta.

**Passo 3 — Barras com agrupamento e ordenação.**

```python
por_cat = (
    df.groupby(["categoria", "canal"], as_index=False)["receita"].sum()
      .sort_values("receita", ascending=False)
)

fig_barra = px.bar(
    por_cat,
    x="receita",
    y="categoria",
    color="canal",
    orientation="h",
    barmode="group",
    labels={"receita": "Receita (R$)", "categoria": "", "canal": "Canal"},
    title="Receita por categoria e canal",
)
fig_barra.update_layout(yaxis={"categoryorder": "total ascending"})
fig_barra.show()
```

:::{admonition} Ordene sempre
:class: tip
Barras em ordem alfabética escondem o ranking. `categoryorder: "total ascending"`
custa uma linha e transforma o gráfico em uma resposta.
:::

**Passo 4 — Dispersão com uma terceira e uma quarta dimensão.**

```python
produto = df.groupby(["produto", "categoria"], as_index=False).agg(
    receita=("receita", "sum"),
    unidades=("unidades", "sum"),
    satisfacao=("satisfacao", "mean"),
)

fig_disp = px.scatter(
    produto,
    x="unidades",
    y="receita",
    size="satisfacao",
    color="categoria",
    hover_name="produto",
    log_y=True,
    labels={"unidades": "Unidades vendidas", "receita": "Receita (R$)"},
    title="Volume × receita por produto",
)
fig_disp.show()
```

**Passo 5 — Empacotar como função para o app.** Esta é a etapa que fecha o
capítulo. No notebook você tinha um trecho solto; no app você quer uma função que
receba o DataFrame **já filtrado** e devolva a figura.

```python
# graficos.py — usado pelo app
import pandas as pd
import plotly.express as px


def grafico_evolucao(df: pd.DataFrame):
    """Receita e lucro agregados por mês."""
    mensal = (
        df.groupby(pd.Grouper(key="data", freq="MS"), as_index=False)
          .agg(receita=("receita", "sum"), lucro=("lucro", "sum"))
    )
    fig = px.line(
        mensal, x="data", y=["receita", "lucro"], markers=True,
        labels={"data": "Mês", "value": "R$", "variable": "Métrica"},
    )
    fig.update_layout(hovermode="x unified", legend_title_text="", height=380)
    return fig
```

E no `app.py`:

```python
import streamlit as st
from graficos import grafico_evolucao

st.plotly_chart(grafico_evolucao(filtrado), use_container_width=True)
```

:::{admonition} Por que separar em `graficos.py`?
:class: tip
Porque a função pode ser testada no notebook, reutilizada em várias páginas e
lida sem o ruído do código de interface. O app fica com uma linha por gráfico —
e um app que se lê em uma tela é um app que se mantém.
:::

:::{card} **Vá além**
O laboratório [`ch06_lab.py`](./labs/ch06_lab.py) traz as cinco figuras já
empacotadas como funções, prontas para copiar para o seu projeto.
:::

## Questões para reflexão

1. A recomendação é estruturar os gráficos no notebook antes do app. Que tipo de
   erro **só** aparece depois da migração para o app, e por quê?
2. Plotly é interativo; Matplotlib é estático. Descreva uma situação em que a
   interatividade **atrapalha** a comunicação do dado.
3. O Plotly Express exige dados tidy. Em que sentido essa exigência é uma
   restrição técnica, e em que sentido ela é uma disciplina analítica útil?
4. Ordenar barras por valor parece óbvio, mas cite um caso em que a ordem
   alfabética (ou cronológica) é a correta.
5. Empacotar cada gráfico como função separa "o que desenhar" de "onde
   desenhar". Que outra separação você faria em um app que cresceu para 800
   linhas?

## Teste você mesmo

:::{dropdown} **Q1.** Por que estruturar os gráficos no notebook antes de levá-los ao dashboard?
**Resposta:** porque o ciclo de depuração no notebook é muito mais rápido e o
erro aparece com contexto. Quando a figura chega ao app já testada, qualquer
problema restante é do app (filtro, layout, cache) e não da figura — o que reduz
o espaço de busca pela causa.
:::

:::{dropdown} **Q2.** O que significa dizer que o Plotly Express espera dados *tidy*?
**Resposta:** que o DataFrame deve estar no formato longo — uma observação por
linha e uma variável por coluna — de modo que colunas possam ser mapeadas
diretamente para `x`, `y`, `color`, `size` etc. A conversão do formato largo para
o longo é feita com `pandas.melt`.
:::

:::{dropdown} **Q3.** Como fazer barras horizontais aparecerem ordenadas por valor?
**Resposta:** `fig.update_layout(yaxis={"categoryorder": "total ascending"})`
(ou `"total descending"`). Sem isso, o Plotly usa a ordem de aparição ou a
alfabética.
:::

:::{dropdown} **Q4.** O que `hovermode="x unified"` faz e por que é útil?
**Resposta:** agrupa todas as séries em um único tooltip ancorado no valor de x
sob o cursor, permitindo comparar as séries no mesmo instante sem passar o mouse
em cada uma.
:::

:::{dropdown} **Q5.** Qual função do Streamlit exibe uma figura do Plotly, e qual argumento faz o gráfico ocupar a largura do container?
**Resposta:** `st.plotly_chart(fig, use_container_width=True)`.
:::

:::{dropdown} **Q6.** Que vantagem prática existe em empacotar cada figura em uma função que recebe o DataFrame filtrado?
**Resposta:** a função pode ser testada isoladamente no notebook, reutilizada em
várias páginas do app e mantida sem o ruído do código de interface. O `app.py`
fica com uma linha por gráfico, muito mais legível.
:::

---

:::{div}
:class: chapter-footer
[← Capítulo 5](../part2/ch05-titulos-markdown-e-status.md) ·
[Índice](../conteudo.md) ·
[Capítulo 7 → Exibindo dados](./ch07-exibindo-dados.md)
:::
