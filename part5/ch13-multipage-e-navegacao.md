---
title: "13. Apps multipágina e navegação"
subject: "Parte 5: Layout e Estrutura"
---

# Apps multipágina e navegação

:::{admonition} O que você vai aprender
:class: tip
- Quando um dashboard precisa deixar de ser uma página só
- As duas abordagens: a pasta `pages/` e a API `st.navigation` + `st.Page`
- Como organizar páginas em seções e definir ícones e URLs
- `st.switch_page` e `st.page_link` para navegação programática
- Como compartilhar dados e estado entre páginas
- Governança de acesso: quem pode ver o quê
:::

:::{div}
:class: run-quick
**Rode este código:** [`part5/labs/ch13_lab.py`](./labs/ch13_lab.py) — um app de
quatro páginas construído com `st.navigation`.
`streamlit run part5/labs/ch13_lab.py`
:::

:::{div}
:class: api-ref
🔗 **Referência da API:** [Navigation and pages](https://docs.streamlit.io/develop/api-reference/navigation)
· [`st.navigation`](https://docs.streamlit.io/develop/api-reference/navigation/st.navigation)
:::

## Visão geral

### Quando dividir

Um único `app.py` funciona bem até certo ponto. Os sinais de que passou da hora:

- o arquivo passou de ~400 linhas e você rola para achar as coisas;
- há mais de 6–8 abas competindo por espaço;
- públicos diferentes usam partes diferentes (diretoria vê o resumo, operação vê
  o detalhe);
- alguma seção é pesada e não deveria ser executada por quem não a usa.

O último ponto é o mais objetivo: **abas executam tudo; páginas não**. Trocar
abas por páginas transfere trabalho para o momento em que ele é realmente pedido.

### Abordagem 1 — A pasta `pages/`

A convenção histórica, ainda suportada e ainda a mais rápida de montar.

```text
meu-dashboard/
├── app.py                   ← página inicial
└── pages/
    ├── 1_📈_Visão_Geral.py
    ├── 2_🗺️_Regiões.py
    └── 3_📋_Dados.py
```

O Streamlit detecta a pasta `pages/` automaticamente e monta o menu na barra
lateral. As regras de nomenclatura:

| No arquivo | Na interface |
| --- | --- |
| Prefixo numérico (`1_`, `2_`) | Define a ordem; não aparece |
| Emoji após o número | Vira o ícone da página |
| Underscores | Viram espaços |
| `1_📈_Visão_Geral.py` | "📈 Visão Geral" |

**Vantagem:** zero configuração. **Limitação:** ordem e rótulos ficam presos ao
nome do arquivo, não há agrupamento em seções, e não dá para esconder páginas por
permissão.

### Abordagem 2 — `st.navigation` + `st.Page`

A API moderna e recomendada. Você declara as páginas em Python, com controle
total.

```python
# app.py — o ponto de entrada
import streamlit as st

st.set_page_config(page_title="Vendas", page_icon="📊", layout="wide")

visao_geral = st.Page("views/visao_geral.py", title="Visão geral",
                      icon=":material/dashboard:", default=True)
regioes     = st.Page("views/regioes.py", title="Regiões",
                      icon=":material/map:")
produtos    = st.Page("views/produtos.py", title="Produtos",
                      icon=":material/inventory_2:")
dados       = st.Page("views/dados.py", title="Dados brutos",
                      icon=":material/table:")
sobre       = st.Page("views/sobre.py", title="Sobre", icon=":material/info:")

pg = st.navigation(
    {
        "Análise": [visao_geral, regioes, produtos],
        "Apoio": [dados, sobre],
    }
)

st.logo("assets/logo.png")
pg.run()
```

| Recurso | `pages/` | `st.navigation` |
| --- | --- | --- |
| Ordem e títulos livres | ❌ | ✅ |
| Agrupamento em seções | ❌ | ✅ |
| Ícones Material Symbols | Só emoji | ✅ (`:material/nome:`) |
| Páginas condicionais (permissão) | ❌ | ✅ |
| Navegação no topo em vez da sidebar | ❌ | ✅ (`position="top"`) |
| Código como fonte da estrutura | ❌ | ✅ |

`st.Page` também aceita uma **função** em vez de um caminho de arquivo, o que
permite manter tudo em um módulo só quando as páginas são curtas.

### Páginas condicionais

Como a lista é montada em Python, ela pode depender de qualquer condição — é
assim que se implementa "nem todo usuário vê tudo".

```python
paginas = {"Análise": [visao_geral, regioes]}

if st.session_state.get("perfil") == "diretoria":
    paginas["Financeiro"] = [margem, custos]

if st.session_state.get("perfil") in ("diretoria", "operacao"):
    paginas.setdefault("Apoio", []).append(dados)

pg = st.navigation(paginas)
pg.run()
```

:::{warning}
Esconder uma página do menu **não** é controle de acesso. A verificação precisa
existir também dentro da página, e o dado sensível não deve nem ser carregado
para quem não pode vê-lo. Voltaremos a isso no
[Capítulo 15](../part6/ch15-roteiro-de-dashboard.md).
:::

### Navegação programática

```python
st.page_link("views/regioes.py", label="Ver detalhe regional", icon="🗺️")
st.page_link("https://docs.streamlit.io", label="Documentação", icon="🔗")

if st.button("Ir para produtos"):
    st.switch_page("views/produtos.py")
```

`st.page_link` desenha um link; `st.switch_page` navega imediatamente, sem
clique adicional.

### Compartilhando dados entre páginas

Três mecanismos, em ordem de preferência:

**1. Uma função cacheada em um módulo comum** — a melhor opção.

```python
# dados.py
import streamlit as st
import pandas as pd

@st.cache_data
def carregar() -> pd.DataFrame:
    return pd.read_csv("data/vendas.csv", parse_dates=["data"])
```

```python
# views/regioes.py
from dados import carregar
df = carregar()          # cache compartilhado entre páginas e sessões
```

**2. `st.session_state`** — para escolhas do usuário que devem persistir na
navegação (o filtro de período selecionado na página anterior).

**3. `st.query_params`** — quando o recorte deve ser compartilhável por link.

:::{important}
O `st.session_state` **sobrevive** à troca de páginas dentro da mesma sessão. Já
os *widgets* de uma página são destruídos ao sair dela: se você quer que o filtro
persista, dê a ele um `key` e leia o valor do `session_state` na outra página.
:::

### Estrutura de projeto recomendada

```text
meu-dashboard/
├── app.py                  ← st.navigation, st.logo, config
├── dados.py                ← carregamento cacheado
├── graficos.py             ← funções que retornam figuras
├── views/
│   ├── visao_geral.py
│   ├── regioes.py
│   ├── produtos.py
│   └── dados_brutos.py
├── assets/
│   └── logo.png
├── data/
│   └── vendas.csv
├── .streamlit/
│   └── config.toml
└── requirements.txt
```

Cada arquivo em `views/` é um script Streamlit comum — sem `if __name__`, sem
função `main()`. O `pg.run()` do `app.py` executa o arquivo da página ativa.

## Mãos à obra

**Passo 1 — O ponto de entrada.**

```python
# app.py
import streamlit as st

st.set_page_config(page_title="Dashboard de Vendas", page_icon="📊",
                   layout="wide", initial_sidebar_state="expanded")

paginas = {
    "Análise": [
        st.Page("views/visao_geral.py", title="Visão geral",
                icon=":material/dashboard:", default=True),
        st.Page("views/regioes.py", title="Regiões", icon=":material/map:"),
    ],
    "Apoio": [
        st.Page("views/dados_brutos.py", title="Dados", icon=":material/table:"),
        st.Page("views/sobre.py", title="Sobre", icon=":material/info:"),
    ],
}

pg = st.navigation(paginas)
pg.run()
```

**Passo 2 — O módulo de dados compartilhado.**

```python
# dados.py
from pathlib import Path
import pandas as pd
import streamlit as st

CAMINHO = Path(__file__).parent / "data" / "vendas.csv"

@st.cache_data(show_spinner="Carregando dados…")
def carregar() -> pd.DataFrame:
    if not CAMINHO.exists():
        raise FileNotFoundError(
            "Rode `python scripts/gerar_dados.py` para gerar o dataset."
        )
    return pd.read_csv(CAMINHO, parse_dates=["data"])
```

**Passo 3 — Uma página.**

```python
# views/visao_geral.py
import streamlit as st
from dados import carregar

df = carregar()

st.title("📊 Visão geral")
st.caption(f"{len(df):,} registros")

k1, k2, k3 = st.columns(3)
k1.metric("Receita", f"R$ {df['receita'].sum():,.0f}", border=True)
k2.metric("Lucro", f"R$ {df['lucro'].sum():,.0f}", border=True)
k3.metric("Pedidos", f"{len(df):,}", border=True)

st.divider()
st.page_link("views/regioes.py", label="Ver detalhamento por região", icon="🗺️")
```

**Passo 4 — Filtro que persiste entre páginas.**

```python
# em qualquer página, na sidebar
opcoes = sorted(df["regiao"].unique())
st.sidebar.multiselect("Região", opcoes, default=opcoes, key="filtro_regiao")

# em outra página, o valor continua lá
selecionadas = st.session_state.get("filtro_regiao", opcoes)
df_filtrado = df[df["regiao"].isin(selecionadas)]
```

Para evitar repetir esse bloco em cada página, extraia-o para uma função em um
módulo `filtros.py` e chame-a no topo de cada view.

:::{card} **Vá além**
O laboratório [`ch13_lab.py`](./labs/ch13_lab.py) monta um app de quatro páginas
usando `st.Page` com **funções** — tudo em um arquivo, para você rodar sem criar
a estrutura de pastas.
:::

## Questões para reflexão

1. Abas executam todo o conteúdo; páginas executam só a ativa. Além do
   desempenho, que diferença isso faz para a **narrativa** do dashboard?
2. `st.navigation` permite esconder páginas por perfil, mas isso não é controle de
   acesso. Onde a verificação real deveria estar, e por quê?
3. Compartilhar dados via função cacheada é preferível a `session_state`.
   Explique essa preferência em termos de quem é dono do dado.
4. Um dashboard de 12 páginas provavelmente tem um problema de design. Que
   pergunta você faria ao cliente antes de aceitar essa estrutura?
5. A pasta `pages/` prende a ordem ao nome do arquivo. Que vantagem existe em uma
   convenção rígida assim, apesar da perda de flexibilidade?

## Teste você mesmo

:::{dropdown} **Q1.** Quais são as duas formas de criar um app multipágina no Streamlit?
**Resposta:** (1) criar uma pasta `pages/` com um arquivo `.py` por página, cujo
nome define ordem, ícone e título; (2) declarar as páginas com `st.Page` e
registrá-las com `st.navigation` no script de entrada, chamando `pg.run()`.
:::

:::{dropdown} **Q2.** Cite duas vantagens de `st.navigation` sobre a pasta `pages/`.
**Resposta:** agrupamento das páginas em seções nomeadas; títulos, ícones e ordem
definidos em código; possibilidade de montar o menu condicionalmente (por perfil
de usuário); suporte a ícones Material Symbols e a navegação no topo. Duas
quaisquer.
:::

:::{dropdown} **Q3.** Como o arquivo `pages/2_🗺️_Regiões.py` aparece no menu?
**Resposta:** como "🗺️ Regiões", na segunda posição. O prefixo numérico define a
ordem e é removido, o emoji vira o ícone e os underscores viram espaços.
:::

:::{dropdown} **Q4.** Qual a diferença entre `st.page_link` e `st.switch_page`?
**Resposta:** `st.page_link` desenha um link clicável na interface;
`st.switch_page` navega imediatamente para a página indicada quando executado,
sem interação adicional — normalmente dentro de um `if st.button(...)`.
:::

:::{dropdown} **Q5.** Qual é a melhor forma de compartilhar um DataFrame entre páginas?
**Resposta:** uma função de carga decorada com `@st.cache_data` em um módulo
comum, importada por todas as páginas. O cache é compartilhado, o dado é
carregado uma vez e cada página recebe uma cópia segura.
:::

:::{dropdown} **Q6.** Esconder uma página do menu é suficiente para proteger dados sensíveis?
**Resposta:** não. Esconder é apenas apresentação — a verificação de permissão
precisa acontecer dentro da própria página, e idealmente o dado sensível nem deve
ser carregado para quem não tem acesso a ele.
:::

---

:::{div}
:class: chapter-footer
[← Capítulo 12](./ch12-layouts-e-containers.md) · [Índice](../conteudo.md) ·
[Capítulo 14 → Temas e Components API](./ch14-temas-e-componentes.md)
:::
