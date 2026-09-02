---
title: "9. Widgets de input"
subject: "Parte 4: Interatividade"
---

# Widgets de input

:::{admonition} O que você vai aprender
:class: tip
- O fluxo de ação de um dashboard: widget → filtro → visualização
- O catálogo completo dos widgets, organizado por tipo de pergunta
- Os argumentos comuns a todos: `label`, `key`, `help`, `disabled`, `on_change`
- Como agrupar filtros em `st.form` para evitar reruns desnecessários
- O padrão de filtragem encadeada que sustenta todo dashboard
:::

:::{div}
:class: run-quick
**Rode este código:** [`part4/labs/ch09_lab.py`](./labs/ch09_lab.py) — catálogo
interativo de widgets + um painel de filtros funcional sobre o dataset de vendas.
`streamlit run part4/labs/ch09_lab.py`
:::

:::{div}
:class: api-ref
🔗 **Referência da API:** [Input widgets](https://docs.streamlit.io/develop/api-reference/widgets)
:::

## Visão geral

### O fluxo de ação de um dashboard

Um dashboard não é uma coleção de gráficos — é uma **ferramenta interativa**. As
visualizações existem para responder a uma pergunta que o usuário formula
manipulando controles. Os widgets são o elemento que torna isso possível:

```text
      widget                filtro                 visualização
  (o usuário pergunta) → (o dado é recortado) → (a resposta aparece)
        ↑                                              │
        └──────────── nova pergunta ←──────────────────┘
```

Sem widgets, você tem um relatório. Com widgets, você tem um dashboard.

### Como um widget funciona

Todo widget faz três coisas ao ser executado:

1. **Desenha** o controle na tela, no ponto em que a linha aparece no script;
2. **Retorna** o valor atual selecionado pelo usuário;
3. **Dispara um rerun** quando esse valor muda.

```python
regiao = st.selectbox("Região", ["Nordeste", "Sudeste", "Sul"])
# a partir daqui, `regiao` contém a string escolhida
```

Na primeira execução, `regiao` vale `"Nordeste"` (o primeiro item, ou o `index=`
indicado). Quando o usuário troca, o script inteiro roda de novo e `regiao` já
vale o novo valor.

### O catálogo, por tipo de pergunta

| A pergunta é… | Widget | Retorna |
| --- | --- | --- |
| Sim/não? | `st.checkbox`, `st.toggle` | `bool` |
| Executar uma ação? | `st.button`, `st.download_button`, `st.link_button` | `bool` (`True` só no rerun do clique) |
| Uma opção entre poucas? | `st.radio`, `st.pills`, `st.segmented_control` | o item escolhido |
| Uma opção entre muitas? | `st.selectbox` | o item escolhido |
| Várias opções? | `st.multiselect` | `list` |
| Um número em uma faixa? | `st.slider`, `st.select_slider` | número (ou tupla, se `value=(a, b)`) |
| Um número exato? | `st.number_input` | `int`/`float` |
| Um texto curto/longo? | `st.text_input`, `st.text_area` | `str` |
| Uma data ou período? | `st.date_input` | `date` ou tupla de datas |
| Uma hora? | `st.time_input` | `time` |
| Um arquivo? | `st.file_uploader` | `UploadedFile` (ou lista) |
| Uma cor? | `st.color_picker` | `str` hexadecimal |
| Uma avaliação? | `st.feedback` | índice da opção (`0`…`n`) |
| Uma foto / um áudio? | `st.camera_input`, `st.audio_input` | arquivo capturado |
| Ir para outra página? | `st.page_link` | — (navega) |

### Argumentos comuns a (quase) todos

| Argumento | Efeito |
| --- | --- |
| `label` | Rótulo acima do controle. Aceita markdown, cores e emojis. |
| `key="algo"` | Identificador estável; também cria `st.session_state["algo"]` |
| `help="..."` | Ícone de interrogação com tooltip |
| `disabled=True` | Desabilita o controle (útil para dependências) |
| `label_visibility` | `"visible"`, `"hidden"` (mantém o espaço) ou `"collapsed"` (remove) |
| `on_change=funcao` | Callback executado **antes** do rerun |
| `placeholder` | Texto de dica em campos vazios |

:::{admonition} Sobre `key`
:class: important
Duas chamadas idênticas ao mesmo widget na mesma página colidem e levantam
`DuplicateWidgetID`. O `key` resolve isso — e, de quebra, expõe o valor em
`st.session_state`, o que será essencial no
[Capítulo 10](./ch10-session-state-e-rerun.md).
:::

### O botão é diferente de todos os outros

```python
if st.button("Processar"):
    st.write("Processando…")     # aparece e SOME no próximo rerun
```

`st.button` retorna `True` **apenas no rerun causado pelo clique**. Qualquer
outra interação na página gera um novo rerun em que o botão vale `False`, e o
conteúdo desaparece. Essa é a fonte número um de confusão em Streamlit.

A correção é registrar a intenção no `session_state`:

```python
if st.button("Processar"):
    st.session_state.processado = True

if st.session_state.get("processado"):
    st.write("Processando…")     # persiste entre reruns
```

### `st.form`: agrupar filtros e adiar o rerun

Por padrão, **cada** widget dispara um rerun. Com cinco filtros e um dataset
grande, o usuário provoca cinco recálculos completos para montar uma única
consulta.

`st.form` resolve: os widgets dentro do formulário não disparam rerun; tudo é
enviado de uma vez ao clicar em `st.form_submit_button`.

```python
with st.form("filtros"):
    col1, col2 = st.columns(2)
    regioes = col1.multiselect("Regiões", opcoes_regiao, default=opcoes_regiao)
    canais = col2.multiselect("Canais", opcoes_canal, default=opcoes_canal)
    periodo = st.date_input("Período", value=(data_min, data_max))
    faixa = st.slider("Ticket (R$)", 0, 5000, (0, 5000))

    enviado = st.form_submit_button("Aplicar filtros", type="primary")

if enviado:
    st.success("Filtros aplicados.")
```

:::{admonition} Quando **não** usar form
:class: warning
O form quebra a sensação de resposta imediata. Se o cálculo é rápido e o usuário
espera ver o efeito de cada ajuste (o caso de um slider exploratório), o form
atrapalha. Use-o quando: o recálculo é caro, os filtros são muitos, ou eles
formam um conjunto que só faz sentido junto.
:::

### Callbacks: `on_change` e `on_click`

Executados **antes** do rerun, com acesso ao `session_state`.

```python
def limpar_filtros():
    st.session_state.regioes = []
    st.session_state.canais = []

st.button("Limpar", on_click=limpar_filtros)
```

Usar o callback para alterar o `session_state` é a forma correta de "resetar"
widgets — tentar atribuir `st.session_state.regioes = []` depois que o widget já
foi desenhado levanta exceção.

## Mãos à obra

**Passo 1 — Um painel de filtros na sidebar.** Filtros vão na barra lateral;
resultados vão na área principal. Essa convenção é quase universal.

```python
import streamlit as st
import pandas as pd

df = pd.read_csv("data/vendas.csv", parse_dates=["data"])

with st.sidebar:
    st.header("Filtros")

    regioes = st.multiselect(
        "Região", sorted(df["regiao"].unique()),
        default=sorted(df["regiao"].unique()),
        help="Deixe vazio para incluir todas.",
    )

    categorias = st.multiselect(
        "Categoria", sorted(df["categoria"].unique()),
        default=sorted(df["categoria"].unique()),
    )

    canal = st.radio("Canal", ["Todos", *sorted(df["canal"].unique())], horizontal=False)

    periodo = st.date_input(
        "Período",
        value=(df["data"].min().date(), df["data"].max().date()),
        min_value=df["data"].min().date(),
        max_value=df["data"].max().date(),
    )

    ticket = st.slider("Ticket (R$)", 0, int(df["receita"].max()),
                       (0, int(df["receita"].max())), step=100)

    st.divider()
    mostrar_tabela = st.toggle("Mostrar tabela detalhada", value=False)
```

**Passo 2 — Aplicar os filtros.** O padrão é uma máscara booleana acumulada.

```python
mask = pd.Series(True, index=df.index)

if regioes:
    mask &= df["regiao"].isin(regioes)
if categorias:
    mask &= df["categoria"].isin(categorias)
if canal != "Todos":
    mask &= df["canal"] == canal
if isinstance(periodo, tuple) and len(periodo) == 2:
    inicio, fim = periodo
    mask &= df["data"].between(pd.Timestamp(inicio), pd.Timestamp(fim))
mask &= df["receita"].between(*ticket)

filtrado = df[mask]
```

**Passo 3 — Tratar o caso vazio.** Um dashboard que mostra gráficos em branco
parece quebrado.

```python
if filtrado.empty:
    st.warning("Nenhum registro corresponde aos filtros. Tente ampliar o período.")
    st.stop()

st.caption(f"{len(filtrado):,} de {len(df):,} registros ({len(filtrado)/len(df):.0%}).")
```

**Passo 4 — Filtros dependentes.** As opções de um widget podem depender da
seleção de outro.

```python
categoria = st.selectbox("Categoria", sorted(df["categoria"].unique()))

produtos_disponiveis = sorted(df.loc[df["categoria"] == categoria, "produto"].unique())
produto = st.selectbox("Produto", produtos_disponiveis)
```

Como o script roda de cima para baixo, o segundo `selectbox` já enxerga a
escolha do primeiro. **Nenhum callback é necessário** — é o modelo de rerun
trabalhando a seu favor.

**Passo 5 — Um botão que persiste.**

```python
if st.button("Gerar relatório", type="primary"):
    st.session_state.relatorio_gerado = True

if st.session_state.get("relatorio_gerado"):
    st.success("Relatório disponível.")
    st.download_button("⬇️ Baixar CSV",
                       filtrado.to_csv(index=False).encode("utf-8-sig"),
                       "relatorio.csv", "text/csv")
```

:::{card} **Vá além**
O laboratório [`ch09_lab.py`](./labs/ch09_lab.py) mostra todos os widgets do
catálogo com o valor retornado ao lado, e traz o painel de filtros completo.
:::

## Questões para reflexão

1. Filtros na sidebar e resultados na área principal virou convenção. Que
   propriedade cognitiva dessa separação a torna eficaz — e quando você a
   quebraria?
2. `st.button` só retorna `True` no rerun do clique. Que decisão de projeto do
   Streamlit isso revela sobre como o framework enxerga "eventos"?
3. Um form melhora o desempenho e piora a sensação de resposta. Como você mediria
   objetivamente qual dos dois pesa mais em um dashboard específico?
4. Filtros dependentes funcionam sem callback graças ao rerun de cima para baixo.
   Que tipo de dependência **circular** esse modelo torna impossível, e isso é uma
   perda ou uma proteção?
5. Cada widget que você adiciona é uma pergunta que o usuário pode fazer. Como
   você decide quando parar de adicionar filtros?

## Teste você mesmo

:::{dropdown} **Q1.** O que um widget retorna, e o que acontece quando o usuário o altera?
**Resposta:** retorna o valor atualmente selecionado. Ao ser alterado, dispara um
rerun completo do script, no qual o widget é recriado já retornando o novo valor.
:::

:::{dropdown} **Q2.** Por que o conteúdo dentro de `if st.button(...)` desaparece quando o usuário mexe em outro widget?
**Resposta:** porque `st.button` retorna `True` apenas no rerun causado pelo
clique. Qualquer outra interação gera um novo rerun em que o botão vale `False`,
e o bloco não é executado. A solução é gravar a intenção em `st.session_state`.
:::

:::{dropdown} **Q3.** Para que serve `st.form`, e qual widget é obrigatório dentro dele?
**Resposta:** agrupa widgets de modo que nenhum deles dispare rerun
individualmente; tudo é enviado de uma vez. É obrigatório haver ao menos um
`st.form_submit_button` dentro do form.
:::

:::{dropdown} **Q4.** Qual widget usar para selecionar várias categorias de uma lista, e o que ele retorna?
**Resposta:** `st.multiselect`, que retorna uma **lista** com os itens
selecionados (vazia se nada foi escolhido).
:::

:::{dropdown} **Q5.** Para que serve o argumento `key`?
**Resposta:** dá ao widget um identificador estável — evitando `DuplicateWidgetID`
quando há widgets iguais na mesma página — e expõe o valor em
`st.session_state["key"]`, permitindo lê-lo e alterá-lo em callbacks.
:::

:::{dropdown} **Q6.** Como implementar um selectbox de produtos cujas opções dependem da categoria escolhida?
**Resposta:** basta ordenar as chamadas no script: o `selectbox` de categoria vem
primeiro; a lista de produtos é calculada filtrando o DataFrame por essa
categoria; o segundo `selectbox` recebe essa lista. O modelo de rerun garante que
a dependência funcione sem callbacks.
:::

---

:::{div}
:class: chapter-footer
[← Capítulo 8](../part3/ch08-funcoes-graficas-e-midia.md) ·
[Índice](../conteudo.md) ·
[Capítulo 10 → Session state e o ciclo de rerun](./ch10-session-state-e-rerun.md)
:::
