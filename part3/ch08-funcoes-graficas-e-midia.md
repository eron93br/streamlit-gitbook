---
title: "8. Funções gráficas e mídia"
subject: "Parte 3: Dados e Gráficos"
---

# Funções gráficas e mídia

:::{admonition} O que você vai aprender
:class: tip
- Exibir imagens de arquivo com `st.image` — o caso mais simples
- Levar figuras do Plotly para a tela com `st.plotly_chart`
- Levar figuras do Matplotlib e do Seaborn com `st.pyplot`
- Os gráficos nativos de uma linha: `st.line_chart`, `st.bar_chart`, `st.area_chart`, `st.scatter_chart`, `st.map`
- Outras bibliotecas suportadas: Altair, Vega-Lite, PyDeck, Graphviz
- Áudio, vídeo, PDF e logotipo
:::

:::{div}
:class: run-quick
**Rode este código:** [`part3/labs/ch08_lab.py`](./labs/ch08_lab.py) — o mesmo
dado desenhado por cinco caminhos diferentes, para comparação.
`streamlit run part3/labs/ch08_lab.py`
:::

:::{div}
:class: api-ref
🔗 **Referência da API:** [Chart elements](https://docs.streamlit.io/develop/api-reference/charts)
· [Media elements](https://docs.streamlit.io/develop/api-reference/media)
· [`st.plotly_chart`](https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart)
:::

## Visão geral

### O caso mais simples: uma imagem de arquivo

Antes dos gráficos, o básico. Como colocar um `.png` ou `.jpg` na tela? Com
`st.image`.

```python
import streamlit as st
from PIL import Image

back_img = Image.open("data/back_churn.png")
st.image(back_img)
```

`st.image` aceita caminho de arquivo (string), URL, objeto `PIL.Image`, array
NumPy ou bytes — e também uma **lista** deles, produzindo uma galeria.

:::{div}
:class: signature
st.image(image, caption=None, width=None, use_container_width=False, clamp=False, channels="RGB", output_format="auto")
:::

```python
st.image("assets/logo.png", width=180)
st.image(url, caption="Fonte: IBGE", use_container_width=True)
st.image([img1, img2, img3], caption=["Antes", "Durante", "Depois"], width=200)
```

:::{admonition} Arrays NumPy e o argumento `channels`
:class: warning
O OpenCV lê imagens em **BGR**, não RGB. Ao exibir um array vindo do
`cv2.imread`, passe `channels="BGR"` — caso contrário azuis e vermelhos aparecem
trocados.
:::

### Três caminhos para um gráfico

O Streamlit oferece três níveis de abstração para desenhar dados. Escolher o
nível certo é metade do trabalho.

| Nível | Função | Controle | Quando usar |
| --- | --- | --- | --- |
| **1. Nativo** | `st.line_chart`, `st.bar_chart`, `st.area_chart`, `st.scatter_chart`, `st.map` | Baixo | Exploração rápida, gráfico de apoio |
| **2. Biblioteca interativa** | `st.plotly_chart`, `st.altair_chart`, `st.vega_lite_chart`, `st.pydeck_chart` | Alto | **O padrão para dashboards** |
| **3. Biblioteca estática** | `st.pyplot` | Total | Gráficos estatísticos específicos, estética de publicação |

### Nível 1 — Gráficos nativos

Aceitam um DataFrame e desenham. Por baixo dos panos usam Vega-Lite.

```python
mensal = df.groupby(pd.Grouper(key="data", freq="MS"))[["receita", "lucro"]].sum()

st.line_chart(mensal)
st.bar_chart(df.groupby("categoria")["receita"].sum())
st.area_chart(mensal, y="receita")
st.scatter_chart(df, x="unidades", y="receita", color="categoria", size="satisfacao")
```

Versões recentes aceitam `x`, `y`, `color`, `size`, `stack` e `horizontal`,
cobrindo bastante coisa. Ainda assim: **sem controle de rótulos de eixo,
formatação de moeda, ordenação customizada ou hover unificado**. Para o gráfico
principal do dashboard, suba de nível.

`st.map` merece nota própria: dado um DataFrame com colunas `lat`/`latitude` e
`lon`/`longitude`, ele desenha os pontos sobre um mapa base, com `size` e
`color` opcionais.

```python
st.map(lojas, latitude="lat", longitude="lon", size="receita", color="#ff4b4b")
```

### Nível 2 — Plotly (o padrão deste livro)

:::{div}
:class: signature
st.plotly_chart(figure_or_data, use_container_width=True, theme="streamlit", key=None, on_select="ignore", selection_mode=("points", "box", "lasso"))
:::

```python
import plotly.express as px

fig = px.bar(por_categoria, x="categoria", y="receita",
             labels={"receita": "Receita (R$)", "categoria": "Categoria"})
fig.update_layout(height=380, margin=dict(t=30, b=0, l=0, r=0))

st.plotly_chart(fig, use_container_width=True)
```

| Argumento | Efeito |
| --- | --- |
| `use_container_width=True` | Ocupa a largura do container. **Quase sempre o que você quer.** Em versões recentes, o equivalente é `width="stretch"` — veja a nota abaixo. |
| `theme="streamlit"` | Aplica a paleta e as fontes do tema do app (padrão). `theme=None` preserva o tema do Plotly. |
| `key="grafico1"` | Identificador estável — obrigatório se houver vários gráficos e você usar seleção |
| `on_select="rerun"` | Torna o gráfico interativo como widget: cliques e seleções voltam para o script |

**Gráfico como filtro.** Assim como tabelas, gráficos Plotly podem virar entrada:

```python
evento = st.plotly_chart(fig, use_container_width=True,
                         on_select="rerun", key="barras")

selecionados = [p["x"] for p in evento.selection["points"]]
if selecionados:
    st.write("Categorias selecionadas:", selecionados)
```

:::{admonition} `use_container_width` está sendo substituído por `width`
:class: warning
Versões recentes do Streamlit trocaram esse argumento por `width`:
`use_container_width=True` vira `width="stretch"`, e
`use_container_width=False` vira `width="content"`. A mudança vale para
`st.plotly_chart`, `st.pyplot`, `st.dataframe`, `st.image`, `st.button` e
outros.

Os exemplos deste livro mantêm a forma antiga por compatibilidade — ela ainda
funciona, emitindo apenas um aviso no terminal. Em projetos novos com versão
recente, prefira `width="stretch"`.
:::

:::{admonition} Margens importam
:class: tip
Figuras do Plotly vêm com margens generosas, pensadas para telas cheias. Em um
dashboard com quatro gráficos, isso desperdiça metade do espaço.
`fig.update_layout(margin=dict(t=30, b=0, l=0, r=0), height=340)` é o ajuste
padrão que vale a pena aplicar em todos.
:::

### Nível 3 — Matplotlib e Seaborn

```python
import matplotlib.pyplot as plt
import seaborn as sns

fig, ax = plt.subplots(figsize=(7, 4))
sns.boxplot(data=df, x="categoria", y="satisfacao", ax=ax)
ax.set_xlabel("")
ax.set_ylabel("Satisfação (1–5)")
ax.tick_params(axis="x", rotation=20)
fig.tight_layout()

st.pyplot(fig, use_container_width=True)
```

:::{important}
Os gráficos do Matplotlib são **estáticos**: uma imagem. Sem hover, sem zoom,
sem legenda clicável. Em compensação, você tem controle total do desenho e acesso
a toda a estatística do Seaborn (boxplot, violin, regplot, pairplot, heatmap de
correlação).

**Sempre crie a figura explicitamente** (`fig, ax = plt.subplots()`) e passe `fig`
para `st.pyplot`. Usar a interface global do pyplot (`plt.plot(...)` seguido de
`st.pyplot()`) é frágil em apps com reruns concorrentes.
:::

### Outras bibliotecas suportadas

| Biblioteca | Função | Nota |
| --- | --- | --- |
| Altair | `st.altair_chart(chart)` | Gramática declarativa, integração excelente |
| Vega-Lite | `st.vega_lite_chart(data, spec)` | Especificação JSON pura |
| PyDeck | `st.pydeck_chart(deck)` | Mapas 3D, grandes volumes de pontos |
| Graphviz | `st.graphviz_chart(dot)` | Fluxogramas, DAGs, diagramas |
| Bokeh | via componente da comunidade | Suporte nativo variou entre versões — confira a API reference da sua versão |

### Outras mídias

```python
st.audio("relatorio.mp3", format="audio/mpeg")
st.video("https://www.youtube.com/watch?v=...")          # aceita URL do YouTube
st.logo("assets/logo.png", icon_image="assets/icone.png") # logo no topo da sidebar
```

`st.logo` é um detalhe de acabamento subestimado: coloca a marca no topo da
barra lateral em todas as páginas, com uma linha.

## Mãos à obra

**Passo 1 — O mesmo dado, três níveis.** Rode e compare.

```python
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("data/vendas.csv", parse_dates=["data"])
por_cat = df.groupby("categoria", as_index=False)["receita"].sum()

aba1, aba2, aba3 = st.tabs(["Nativo", "Plotly", "Matplotlib"])

with aba1:
    st.bar_chart(por_cat, x="categoria", y="receita")
    st.caption("Uma linha. Sem controle de formatação.")

with aba2:
    fig = px.bar(por_cat.sort_values("receita"), x="receita", y="categoria",
                 orientation="h", labels={"receita": "Receita (R$)", "categoria": ""})
    fig.update_layout(height=340, margin=dict(t=20, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Interativo, ordenado, rotulado. O padrão para dashboards.")

with aba3:
    fig_mpl, ax = plt.subplots(figsize=(6, 3.4))
    sns.barplot(data=por_cat.sort_values("receita"), x="receita", y="categoria",
                ax=ax, color="#ff4b4b")
    ax.set_xlabel("Receita (R$)")
    ax.set_ylabel("")
    fig_mpl.tight_layout()
    st.pyplot(fig_mpl, use_container_width=True)
    st.caption("Estático, mas com controle total do desenho.")
```

**Passo 2 — Uma imagem de contexto.** Muitos dashboards abrem com uma imagem de
capa ou um diagrama do processo.

```python
from PIL import Image
from pathlib import Path

capa = Path("assets/capa.png")
if capa.exists():
    st.image(Image.open(capa), use_container_width=True)
else:
    st.info("Coloque uma imagem em `assets/capa.png` para exibi-la aqui.")
```

**Passo 3 — Um gráfico estatístico que só o Seaborn faz bem.**

```python
fig, ax = plt.subplots(figsize=(6, 4))
corr = df[["unidades", "preco_unitario", "receita", "lucro", "satisfacao"]].corr()
sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", center=0, ax=ax)
ax.set_title("Correlação entre variáveis")
fig.tight_layout()
st.pyplot(fig)
```

**Passo 4 — Gráfico como filtro (mestre-detalhe).**

```python
fig = px.bar(por_cat, x="categoria", y="receita")
evento = st.plotly_chart(fig, use_container_width=True,
                         on_select="rerun", key="cat_bar")

pontos = evento.selection.get("points", [])
if pontos:
    cat = pontos[0]["x"]
    st.subheader(f"Detalhe · {cat}")
    st.dataframe(
        df[df["categoria"] == cat].nlargest(10, "receita"),
        use_container_width=True, hide_index=True,
    )
else:
    st.caption("Clique em uma barra para ver os maiores pedidos da categoria.")
```

:::{card} **Vá além**
O laboratório [`ch08_lab.py`](./labs/ch08_lab.py) executa os quatro passos e
inclui exemplos de `st.map` e `st.graphviz_chart`.
:::

## Questões para reflexão

1. Os gráficos nativos resolvem em uma linha o que o Plotly resolve em cinco. Que
   critério objetivo você usaria para decidir, em cada gráfico do seu dashboard,
   qual nível usar?
2. `st.pyplot` produz imagens estáticas. Cite um gráfico estatístico para o qual
   você aceitaria abrir mão da interatividade — e justifique.
3. Um gráfico com `on_select="rerun"` vira um filtro. Que problema de
   descobribilidade isso cria (como o usuário sabe que pode clicar)?
4. O argumento `theme="streamlit"` sobrescreve as cores da sua figura Plotly. Em
   que situação você preferiria `theme=None`?
5. `st.image` aceita URL. Que dependências e riscos isso introduz em um dashboard
   que será usado dentro de uma rede corporativa?

## Teste você mesmo

:::{dropdown} **Q1.** Qual função exibe um arquivo `.png` na tela, e o que ela aceita como entrada?
**Resposta:** `st.image`. Aceita caminho de arquivo, URL, objeto `PIL.Image`,
array NumPy, bytes — e listas desses tipos, produzindo uma galeria.
:::

:::{dropdown} **Q2.** Qual argumento faz uma figura Plotly ocupar toda a largura do container?
**Resposta:** `use_container_width=True` em `st.plotly_chart(fig, use_container_width=True)`.
:::

:::{dropdown} **Q3.** Como exibir uma figura do Matplotlib/Seaborn, e qual é a boa prática ao criá-la?
**Resposta:** com `st.pyplot(fig)`. A boa prática é criar a figura
explicitamente — `fig, ax = plt.subplots()` — e passar o objeto `fig`, em vez de
depender da figura global do pyplot, que é frágil sob reruns concorrentes.
:::

:::{dropdown} **Q4.** Cite duas bibliotecas de visualização além de Plotly e Matplotlib que o Streamlit suporta nativamente.
**Resposta:** Altair (`st.altair_chart`), Vega-Lite (`st.vega_lite_chart`),
PyDeck (`st.pydeck_chart`) e Graphviz (`st.graphviz_chart`). Duas quaisquer.
:::

:::{dropdown} **Q5.** Qual a limitação principal dos gráficos nativos (`st.bar_chart` e similares)?
**Resposta:** pouco controle de apresentação — rótulos de eixo, formatação de
valores, ordenação customizada, hover unificado e ajustes finos de layout não
estão disponíveis. São ótimos para exploração rápida, insuficientes para o
gráfico principal de um dashboard.
:::

:::{dropdown} **Q6.** Uma imagem lida com OpenCV aparece com as cores trocadas. Por quê, e como corrigir?
**Resposta:** o OpenCV lê em ordem BGR, enquanto o `st.image` assume RGB por
padrão. Corrige-se passando `channels="BGR"` — ou convertendo o array com
`cv2.cvtColor(img, cv2.COLOR_BGR2RGB)`.
:::

---

:::{div}
:class: chapter-footer
[← Capítulo 7](./ch07-exibindo-dados.md) · [Índice](../conteudo.md) ·
[Capítulo 9 → Widgets de input](../part4/ch09-widgets-de-input.md)
:::
