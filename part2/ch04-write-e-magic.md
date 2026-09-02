---
title: "4. st.write e os magic commands"
subject: "Parte 2: Elementos de Texto"
---

# `st.write` e os magic commands

:::{admonition} O que você vai aprender
:class: tip
- O que são as **funções de display** e por que o Streamlit tem tantas
- Como `st.write` decide sozinho o que fazer com cada tipo de objeto
- O que são **magic commands** e quando eles ajudam ou atrapalham
- Quando abandonar o `st.write` em favor de uma função específica
- Como exibir respostas de LLM em streaming com `st.write_stream`
:::

:::{div}
:class: run-quick
**Rode este código:** [`part2/labs/ch04_lab.py`](./labs/ch04_lab.py) — um app que
passa o mesmo dado por `st.write`, magic e funções específicas, lado a lado.
`streamlit run part2/labs/ch04_lab.py`
:::

:::{div}
:class: api-ref
🔗 **Referência da API:** [Write and magic](https://docs.streamlit.io/develop/api-reference/write-magic)
· [`st.write`](https://docs.streamlit.io/develop/api-reference/write-magic/st.write)
:::

## Visão geral

### As funções de display

O Streamlit oferece um conjunto de funções para colocar conteúdo na tela: texto,
tabelas, imagens, gráficos, métricas, mensagens de status. Coletivamente elas
são chamadas de **funções de display** — cada uma sabe renderizar um tipo de
coisa, com o layout e os controles apropriados.

`st.write` é a porta de entrada desse conjunto. Ela é **polimórfica**: examina o
tipo do objeto recebido e delega para a função especializada correspondente.

### O que `st.write` faz com cada tipo

| Você passa | `st.write` renderiza como |
| --- | --- |
| `str` | Markdown (com suporte a emoji, LaTeX, links) |
| `int`, `float` | Número formatado |
| `pandas.DataFrame` / `Series` | Tabela interativa (equivale a `st.dataframe`) |
| `dict`, `list` | Visualizador JSON expansível |
| Figura Plotly | Gráfico interativo (equivale a `st.plotly_chart`) |
| Figura Matplotlib | Imagem estática (equivale a `st.pyplot`) |
| Figura Altair / Vega-Lite | Gráfico interativo |
| Exceção | Traceback formatado |
| Função, módulo, classe | Documentação (`st.help`) |
| Vários argumentos | Renderiza um após o outro, na mesma linha lógica |

```python
import streamlit as st
import pandas as pd

st.write(1234)
st.write("Texto com **negrito** e :blue[cor]")
st.write(pd.DataFrame({
    "primeira coluna": [1, 2, 3, 4],
    "segunda coluna": [10, 20, 30, 40],
}))
st.write({"chave": "valor", "lista": [1, 2, 3]})
```

### Magic commands

O Streamlit vai um passo além: se você deixar uma **variável ou literal sozinha
em uma linha**, no nível superior do script, ele chama `st.write` nela
automaticamente. Isso se chama *magic*.

```python
import streamlit as st
import pandas as pd

df = pd.DataFrame({"a": [1, 2, 3]})

"### Meu relatório"        # ← vira st.write("### Meu relatório")
df                          # ← vira st.write(df)
1 + 1                       # ← vira st.write(2)
```

É idêntico ao comportamento do Jupyter, onde a última expressão da célula é
exibida. Por isso o magic é confortável para quem vem de notebooks.

:::{admonition} Magic: use com moderação
:class: warning
O magic é ótimo para prototipar e péssimo para manter. Em um app de 300 linhas,
uma string solta no meio do código parece **um erro de digitação**, não uma
intenção — e ferramentas de lint vão sinalizá-la como *statement without
effect*.

**Recomendação deste livro:** use magic no rascunho, converta para `st.write` ou
para a função específica antes de entregar. O magic pode ser desligado no
`config.toml` com `magicEnabled = false`.
:::

### Quando `st.write` **não** é a melhor escolha

`st.write` é conveniente porque adivinha. Mas adivinhar significa **abrir mão do
controle**: você não passa os argumentos específicos da função de destino.

| Situação | Em vez de `st.write` | Use |
| --- | --- | --- |
| Tabela com colunas formatadas | `st.write(df)` | `st.dataframe(df, column_config=...)` |
| Gráfico Plotly ocupando a largura | `st.write(fig)` | `st.plotly_chart(fig, use_container_width=True)` |
| Título semântico da página | `st.write("# Título")` | `st.title("Título")` |
| Texto sem interpretação de markdown | `st.write(txt)` | `st.text(txt)` |
| Código com destaque de sintaxe | `st.write(codigo)` | `st.code(codigo, language="python")` |
| Mensagem de erro destacada | `st.write("Erro!")` | `st.error("Erro!")` |

:::{admonition} Regra prática
:class: tip
**Prototipe com `st.write`; entregue com a função específica.**
:::

### `st.write_stream`

Para saída que chega aos poucos — tipicamente a resposta de um modelo de
linguagem — existe `st.write_stream`, que consome um gerador e escreve na tela
conforme os pedaços chegam, com efeito de digitação.

```python
import time
import streamlit as st

def gerar_resposta():
    for palavra in "O dashboard mostra a receita por região.".split():
        yield palavra + " "
        time.sleep(0.05)

if st.button("Gerar"):
    texto_completo = st.write_stream(gerar_resposta)
```

A função **retorna** o texto completo ao final, o que é conveniente para guardar
no histórico da conversa.

## Mãos à obra

**Passo 1 — Um objeto, três renderizações.** Carregue o dataset e compare.

```python
import streamlit as st
import pandas as pd

df = pd.read_csv("data/vendas.csv", parse_dates=["data"])
resumo = df.groupby("regiao", as_index=False)["receita"].sum()

st.subheader("1 · st.write — adivinha o tipo")
st.write(resumo)

st.subheader("2 · magic — a variável sozinha na linha")
resumo

st.subheader("3 · st.dataframe — controle explícito")
st.dataframe(
    resumo,
    use_container_width=True,
    hide_index=True,
    column_config={
        "regiao": "Região",
        "receita": st.column_config.NumberColumn("Receita", format="R$ %.2f"),
    },
)
```

Os três produzem uma tabela. Só o terceiro produz a tabela que você quer mostrar
para outra pessoa.

**Passo 2 — `st.write` com múltiplos argumentos.**

```python
regiao = "Nordeste"
total = 1_284_500.0

st.write("Receita da região", regiao, "→", f"R$ {total:,.2f}")
```

Os argumentos são renderizados em sequência. Útil para intercalar texto e
variáveis sem montar f-strings longas — mas note que a formatação fina (moeda,
separador de milhar) continua sendo sua responsabilidade.

**Passo 3 — Markdown embutido em `st.write`.** Strings passam por markdown, o
que inclui a sintaxe de cor e emoji do Streamlit:

```python
st.write("Status: :green[**dentro da meta**] :white_check_mark:")
st.write("Variação: :red[-12,4%] :arrow_down:")
st.write(r"Margem: $m = \frac{lucro}{receita}$")
```

**Passo 4 — Inspecionar objetos.** `st.write` em um módulo ou função exibe a
documentação — atalho útil durante o desenvolvimento:

```python
import plotly.express as px
st.write(px.bar)      # mostra a assinatura e a docstring
```

:::{card} **Vá além**
O laboratório [`ch04_lab.py`](./labs/ch04_lab.py) monta uma galeria com todos os
tipos que `st.write` reconhece, para você ver cada renderização.
:::

## Questões para reflexão

1. `st.write` adivinha o tipo do objeto. Cite um caso em que essa adivinhação
   produz um resultado tecnicamente correto mas comunicativamente ruim.
2. Magic commands tornam o script mais parecido com um notebook. Isso é uma
   vantagem pedagógica e um risco de manutenção ao mesmo tempo — em que momento
   do ciclo de vida de um app a balança vira?
3. Se `st.write(df)` e `st.dataframe(df)` produzem a mesma tabela, por que as
   duas funções existem? O que a existência da segunda revela sobre a filosofia
   da API?
4. `st.write_stream` retorna o texto completo ao final. Por que essa decisão de
   projeto é importante para quem constrói um chat?
5. Um app usa `st.write` em 100% das saídas. Sem ver o código, o que você
   consegue prever sobre a qualidade visual desse app e sobre a facilidade de
   ajustá-lo?

## Teste você mesmo

:::{dropdown} **Q1.** O que significa dizer que `st.write` é polimórfica?
**Resposta:** ela inspeciona o tipo do objeto recebido e delega para a função de
display apropriada — `st.dataframe` para um DataFrame, `st.plotly_chart` para uma
figura Plotly, `st.markdown` para uma string, `st.json` para um dicionário, e
assim por diante.
:::

:::{dropdown} **Q2.** O que é um magic command no Streamlit?
**Resposta:** é o comportamento em que uma variável ou literal deixada sozinha em
uma linha, no nível superior do script, é automaticamente passada para
`st.write`. Funciona como a última expressão de uma célula de notebook.
:::

:::{dropdown} **Q3.** Cite duas razões para preferir `st.dataframe` a `st.write` ao exibir uma tabela final.
**Resposta:** (a) `st.dataframe` aceita argumentos como `column_config`,
`hide_index`, `use_container_width` e `height`, que dão controle sobre a
apresentação; (b) o código fica explícito sobre a intenção, facilitando a
manutenção e a revisão. `st.write` não repassa esses argumentos.
:::

:::{dropdown} **Q4.** O que acontece ao chamar `st.write("a", 1, df)`?
**Resposta:** os três argumentos são renderizados em sequência na página — a
string como markdown, o número formatado e o DataFrame como tabela interativa.
:::

:::{dropdown} **Q5.** Para que serve `st.write_stream` e o que ela retorna?
**Resposta:** consome um gerador (ou stream) e escreve o conteúdo na tela à
medida que os pedaços chegam, com efeito de digitação — típico de respostas de
LLM. Ao final, retorna o texto completo concatenado, útil para armazenar no
histórico.
:::

:::{dropdown} **Q6.** Como desativar os magic commands em um projeto?
**Resposta:** definindo `magicEnabled = false` na seção `[runner]` do arquivo
`.streamlit/config.toml`.
:::

---

:::{div}
:class: chapter-footer
[← Capítulo 3](../part1/ch03-primeiro-app-modelo-de-execucao.md) ·
[Índice](../conteudo.md) ·
[Capítulo 5 → Títulos, markdown e mensagens de status](./ch05-titulos-markdown-e-status.md)
:::
