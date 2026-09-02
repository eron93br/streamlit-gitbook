---
title: "7. Exibindo dados: dataframe, table e metric"
subject: "Parte 3: Dados e Gráficos"
---

# Exibindo dados: dataframe, table e metric

:::{admonition} O que você vai aprender
:class: tip
- A diferença entre `st.dataframe`, `st.table`, `st.data_editor` e `st.json`
- Como formatar colunas com `st.column_config` — moeda, porcentagem, barra, link, gráfico
- Como construir uma **linha de KPIs** com `st.metric` e o argumento `delta`
- Como capturar a seleção do usuário em uma tabela (`on_select`)
- Como oferecer download do recorte filtrado com `st.download_button`
:::

:::{div}
:class: run-quick
**Rode este código:** [`part3/labs/ch07_lab.py`](./labs/ch07_lab.py) — KPIs,
tabela formatada, editor e download em um só app.
`streamlit run part3/labs/ch07_lab.py`
:::

:::{div}
:class: api-ref
🔗 **Referência da API:** [Data elements](https://docs.streamlit.io/develop/api-reference/data)
· [`st.column_config`](https://docs.streamlit.io/develop/api-reference/data/st.column_config)
:::

## Visão geral

### Quatro formas de mostrar dados

| Função | O que é | Quando usar |
| --- | --- | --- |
| `st.dataframe` | Tabela **interativa**: ordena, redimensiona, busca, exporta, rola | O padrão para qualquer tabela de dados |
| `st.table` | Tabela **estática**, renderizada por inteiro | Poucas linhas que precisam estar todas visíveis |
| `st.data_editor` | Tabela **editável** pelo usuário; devolve o DataFrame alterado | Simulação, correção manual, entrada de premissas |
| `st.json` | Visualizador de JSON expansível | Dicionários, respostas de API, configurações |

:::{warning}
`st.table` renderiza **todas** as linhas de uma vez, sem paginação. Passar um
DataFrame de 10.000 linhas trava o navegador. Use `st.dataframe`, que
virtualiza a rolagem.
:::

### `st.dataframe`: os argumentos que importam

:::{div}
:class: signature
st.dataframe(data, width=None, height=None, use_container_width=False, hide_index=None, column_order=None, column_config=None, selection_mode="multi-row", on_select="ignore")
:::

| Argumento | Efeito |
| --- | --- |
| `use_container_width=True` | A tabela ocupa toda a largura disponível |
| `hide_index=True` | Esconde o índice numérico do pandas |
| `column_order=[...]` | Reordena e/ou filtra as colunas exibidas |
| `column_config={...}` | Formatação por coluna — o recurso mais útil |
| `height=400` | Altura fixa em pixels |
| `on_select="rerun"` | Torna a tabela um widget: a seleção do usuário volta para o script |

### `st.column_config`: formatação que muda tudo

Uma tabela crua mostra `1284500.0`. Uma tabela configurada mostra
`R$ 1.284.500,00`. É a mesma informação e uma diferença enorme de leitura.

```python
st.dataframe(
    resumo,
    use_container_width=True,
    hide_index=True,
    column_config={
        "regiao": st.column_config.TextColumn("Região", width="medium"),
        "receita": st.column_config.NumberColumn("Receita", format="R$ %.2f"),
        "margem": st.column_config.ProgressColumn(
            "Margem", format="%.1f%%", min_value=0, max_value=100
        ),
        "evolucao": st.column_config.LineChartColumn("Tendência 12m"),
        "link": st.column_config.LinkColumn("Detalhe", display_text="abrir"),
        "ativo": st.column_config.CheckboxColumn("Ativo"),
        "atualizado": st.column_config.DatetimeColumn("Atualizado", format="DD/MM/YYYY"),
    },
)
```

| Tipo de coluna | Para quê |
| --- | --- |
| `TextColumn` | Texto, com largura e `max_chars` |
| `NumberColumn` | Números com `format` (estilo `printf`), `min_value`, `step` |
| `ProgressColumn` | Barra de preenchimento — ótima para percentuais |
| `LineChartColumn` / `BarChartColumn` / `AreaChartColumn` | *Sparklines* a partir de uma coluna de listas |
| `LinkColumn` | URLs clicáveis, com texto customizado |
| `CheckboxColumn` | Booleanos como caixas |
| `DateColumn` / `DatetimeColumn` / `TimeColumn` | Datas com formato |
| `SelectboxColumn` | Lista de opções (útil no `data_editor`) |
| `ImageColumn` | Miniaturas a partir de URLs |

### `st.metric`: a linha de KPIs

Um dashboard começa com números grandes. `st.metric` desenha um valor com
rótulo e, opcionalmente, uma variação colorida.

:::{div}
:class: signature
st.metric(label, value, delta=None, delta_color="normal", help=None, border=False)
:::

```python
col1, col2, col3, col4 = st.columns(4)
col1.metric("Receita", "R$ 9,7 mi", "+12,4%")
col2.metric("Lucro", "R$ 3,1 mi", "+8,1%")
col3.metric("Ticket médio", "R$ 812", "-2,3%")
col4.metric("Satisfação", "4,1 / 5", "0,0")
```

| Argumento | Comportamento |
| --- | --- |
| `delta` | Texto da variação. Positivo → verde e seta para cima; negativo → vermelho e seta para baixo |
| `delta_color="inverse"` | Inverte as cores — use para métricas em que **subir é ruim** (churn, custo, tempo de resposta) |
| `delta_color="off"` | Mostra a variação em cinza, sem julgamento |
| `border=True` | Desenha uma borda ao redor do cartão |

:::{admonition} A armadilha do delta
:class: warning
O Streamlit assume que "subir é bom". Para **taxa de cancelamento**, **custo** ou
**tempo médio de atendimento**, um delta positivo verde comunica exatamente o
contrário do que você quer. Use `delta_color="inverse"`.
:::

### `st.data_editor`: quando o usuário escreve

`st.data_editor` devolve o DataFrame **depois** das edições do usuário. É o
caminho para simulações ("e se a meta fosse 10% maior?") e correções pontuais.

```python
editado = st.data_editor(
    premissas,
    num_rows="dynamic",              # permite adicionar/remover linhas
    disabled=["categoria"],          # colunas somente leitura
    column_config={
        "meta": st.column_config.NumberColumn("Meta (R$)", min_value=0, step=1000),
    },
)
st.write("Meta total:", editado["meta"].sum())
```

:::{important}
O `data_editor` altera apenas o DataFrame **em memória, naquela sessão**. Nada é
gravado em disco ou banco automaticamente — se você quer persistir, precisa
escrever o código de gravação explicitamente.
:::

### Tabelas como widget: `on_select`

Com `on_select="rerun"`, a tabela deixa de ser saída e passa a ser **entrada**: a
seleção do usuário dispara um rerun e fica disponível no valor de retorno.

```python
evento = st.dataframe(
    produtos,
    on_select="rerun",
    selection_mode="single-row",
    hide_index=True,
)

linhas = evento.selection.rows
if linhas:
    produto = produtos.iloc[linhas[0]]["produto"]
    st.subheader(f"Detalhe de {produto}")
    st.plotly_chart(grafico_produto(df, produto), use_container_width=True)
else:
    st.info("Selecione uma linha para ver o detalhamento.")
```

Esse é o padrão **mestre-detalhe**, e é o que separa um dashboard de uma
apresentação de slides.

## Mãos à obra

**Passo 1 — A linha de KPIs.**

```python
import streamlit as st
import pandas as pd

df = pd.read_csv("data/vendas.csv", parse_dates=["data"])

atual = df[df["data"].dt.year == 2025]
anterior = df[df["data"].dt.year == 2024]

def variacao(serie_atual, serie_anterior):
    if serie_anterior == 0:
        return None
    return f"{(serie_atual / serie_anterior - 1):+.1%}"

c1, c2, c3, c4 = st.columns(4)
c1.metric("Receita", f"R$ {atual['receita'].sum():,.0f}",
          variacao(atual["receita"].sum(), anterior["receita"].sum()), border=True)
c2.metric("Lucro", f"R$ {atual['lucro'].sum():,.0f}",
          variacao(atual["lucro"].sum(), anterior["lucro"].sum()), border=True)
c3.metric("Unidades", f"{atual['unidades'].sum():,}",
          variacao(atual["unidades"].sum(), anterior["unidades"].sum()), border=True)
c4.metric("Custo", f"R$ {atual['custo'].sum():,.0f}",
          variacao(atual["custo"].sum(), anterior["custo"].sum()),
          delta_color="inverse", border=True)   # ← subir custo é ruim
```

**Passo 2 — A tabela de apoio, formatada.**

```python
resumo = (
    df.groupby("categoria", as_index=False)
      .agg(receita=("receita", "sum"),
           lucro=("lucro", "sum"),
           unidades=("unidades", "sum"))
)
resumo["margem_pct"] = (resumo["lucro"] / resumo["receita"] * 100).round(1)
resumo = resumo.sort_values("receita", ascending=False)

st.dataframe(
    resumo,
    use_container_width=True,
    hide_index=True,
    column_config={
        "categoria": "Categoria",
        "receita": st.column_config.NumberColumn("Receita", format="R$ %.0f"),
        "lucro": st.column_config.NumberColumn("Lucro", format="R$ %.0f"),
        "unidades": st.column_config.NumberColumn("Unidades", format="%d"),
        "margem_pct": st.column_config.ProgressColumn(
            "Margem", format="%.1f%%", min_value=0, max_value=60
        ),
    },
)
```

**Passo 3 — Sparklines por categoria.** Uma coluna cujo conteúdo é uma **lista**
vira um minigráfico.

```python
serie = (
    df.groupby(["categoria", pd.Grouper(key="data", freq="MS")])["receita"]
      .sum()
      .groupby(level=0)
      .apply(list)
      .rename("tendencia")
      .reset_index()
)
tabela = resumo.merge(serie, on="categoria")

st.dataframe(
    tabela,
    use_container_width=True,
    hide_index=True,
    column_config={
        "tendencia": st.column_config.LineChartColumn("Tendência mensal", y_min=0),
        "receita": st.column_config.NumberColumn("Receita", format="R$ %.0f"),
    },
    column_order=["categoria", "receita", "tendencia"],
)
```

**Passo 4 — Download do recorte.** Todo dashboard deveria permitir levar o dado
embora.

```python
csv = resumo.to_csv(index=False).encode("utf-8-sig")   # utf-8-sig abre certo no Excel
st.download_button(
    "⬇️ Baixar resumo (CSV)",
    data=csv,
    file_name="resumo_categorias.csv",
    mime="text/csv",
)
```

:::{admonition} `utf-8-sig`
:class: tip
O Excel no Windows interpreta CSV sem BOM como Latin-1 e quebra acentos. Gravar
em `utf-8-sig` adiciona o BOM e resolve — um detalhe que evita muitos e-mails.
:::

:::{card} **Vá além**
O laboratório [`ch07_lab.py`](./labs/ch07_lab.py) reúne os quatro passos e
adiciona um exemplo de mestre-detalhe com `on_select`.
:::

## Questões para reflexão

1. `st.table` renderiza tudo de uma vez e `st.dataframe` virtualiza. Além do
   desempenho, existe alguma situação em que a renderização completa é
   *desejável*?
2. `st.metric` colore o delta assumindo que subir é bom. Que outras suposições
   embutidas em componentes de dashboard você consegue identificar, e como elas
   podem induzir a erro?
3. O `data_editor` altera apenas a cópia em memória. Que expectativa isso cria no
   usuário, e como você a gerenciaria na interface?
4. Formatar uma coluna como `ProgressColumn` transforma um número em uma barra.
   Em que ponto a formatação deixa de ajudar a leitura e começa a distorcê-la?
5. Oferecer download do recorte filtrado é conveniente e é também uma porta de
   saída de dados. Quais controles de governança você adicionaria em um contexto
   corporativo?

## Teste você mesmo

:::{dropdown} **Q1.** Qual a diferença fundamental entre `st.dataframe` e `st.table`?
**Resposta:** `st.dataframe` é interativa e virtualizada — ordena, rola, busca e
suporta muitas linhas sem travar. `st.table` é estática e renderiza todas as
linhas de uma vez, adequada apenas a tabelas pequenas.
:::

:::{dropdown} **Q2.** Como exibir a coluna `receita` formatada como moeda?
**Resposta:** via `column_config`:
`st.dataframe(df, column_config={"receita": st.column_config.NumberColumn("Receita", format="R$ %.2f")})`.
:::

:::{dropdown} **Q3.** Para uma métrica de custo, qual argumento de `st.metric` evita que um aumento apareça em verde?
**Resposta:** `delta_color="inverse"`, que inverte a lógica de cor — delta
positivo fica vermelho e negativo fica verde. `delta_color="off"` deixa em cinza.
:::

:::{dropdown} **Q4.** O que `st.data_editor` retorna, e o que ele **não** faz?
**Resposta:** retorna o DataFrame com as edições feitas pelo usuário naquela
sessão. Ele **não** persiste nada em disco ou banco — a gravação precisa ser
codificada explicitamente.
:::

:::{dropdown} **Q5.** Como transformar uma tabela em um filtro do próprio dashboard?
**Resposta:** passando `on_select="rerun"` (com `selection_mode` adequado). A
seleção do usuário dispara um rerun e volta no objeto de retorno, em
`evento.selection.rows` (ou `.columns`), permitindo o padrão mestre-detalhe.
:::

:::{dropdown} **Q6.** Que tipo de coluna produz um minigráfico dentro da tabela, e qual formato o dado precisa ter?
**Resposta:** `st.column_config.LineChartColumn` (também `BarChartColumn` e
`AreaChartColumn`). A célula precisa conter uma **lista** de números — tipicamente
produzida com um `groupby(...).apply(list)`.
:::

---

:::{div}
:class: chapter-footer
[← Capítulo 6](./ch06-plotly-express.md) · [Índice](../conteudo.md) ·
[Capítulo 8 → Funções gráficas e mídia](./ch08-funcoes-graficas-e-midia.md)
:::
