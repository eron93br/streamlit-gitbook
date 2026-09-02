---
title: "3. O primeiro app e o modelo de execução"
subject: "Parte 1: Motivação e Ambiente"
---

# O primeiro app e o modelo de execução

:::{admonition} O que você vai aprender
:class: tip
- Como o Streamlit executa seu script: o ciclo de **rerun**
- O que dispara um rerun e o que não dispara
- Configurar a página com `st.set_page_config` — e por que ela vem primeiro
- A anatomia de um arquivo de app bem organizado
- Como interromper a execução com `st.stop`
:::

:::{div}
:class: run-quick
**Rode este código:** [`part1/labs/ch03_lab.py`](./labs/ch03_lab.py) — um app que
**mostra** o rerun acontecendo, contando as execuções na sua frente.
`streamlit run part1/labs/ch03_lab.py`
:::

:::{div}
:class: api-ref
🔗 **Referência da API:** [Execution flow](https://docs.streamlit.io/develop/api-reference/execution-flow)
· [`st.set_page_config`](https://docs.streamlit.io/develop/api-reference/configuration/st.set_page_config)
:::

## Visão geral

### O ciclo de rerun

Este é o conceito central do Streamlit, e o único que realmente precisa ser
internalizado:

> **Toda vez que o usuário interage com um widget — ou você salva o arquivo — o
> Streamlit descarta a página e reexecuta o script inteiro, da primeira linha à
> última.**

Não há callbacks obrigatórios, não há componentes que se atualizam sozinhos. Há
um script que roda de novo, e uma página que é redesenhada com o resultado.

```text
usuário move o slider
        ↓
Streamlit reexecuta app.py do início
        ↓
o widget slider é recriado, agora com o novo valor
        ↓
todo o código abaixo dele roda com esse valor
        ↓
a página é redesenhada
```

Isso é radicalmente diferente do modelo de eventos do JavaScript ou dos
callbacks do Dash — e é o que torna o código do Streamlit legível de cima para
baixo, como um notebook.

### As três consequências

Praticamente toda dúvida de iniciante em Streamlit é uma das três consequências
abaixo.

**1. Variáveis locais não sobrevivem entre reruns.**

```python
contador = 0                       # ← redefinido como 0 a cada rerun
if st.button("Somar 1"):
    contador += 1
st.write(contador)                 # sempre mostra 0 ou 1, nunca 2
```

A solução é `st.session_state`, o dicionário que persiste entre reruns —
assunto do [Capítulo 10](../part4/ch10-session-state-e-rerun.md).

**2. Código lento roda de novo a cada clique.**

Se a linha `pd.read_csv("arquivo_de_2GB.csv")` está no topo do script, ela é
executada toda vez que alguém mexe em qualquer widget. A solução é
`st.cache_data`, no [Capítulo 11](../part4/ch11-cache-e-performance.md).

**3. A ordem das linhas é a ordem da tela.**

O que vem antes no script aparece acima na página. Isso é uma vantagem — o
layout é o código — mas significa que você não pode usar uma variável definida
depois do ponto em que ela é exibida. Para "reservar um lugar" na tela e
preenchê-lo mais tarde, existe `st.empty()`
([Capítulo 12](../part5/ch12-layouts-e-containers.md)).

### O que dispara um rerun

| Ação | Dispara rerun? |
| --- | --- |
| Usuário mexe em um widget (slider, selectbox, botão…) | ✅ Sim |
| Você salva o arquivo `.py` | ✅ Sim (com *Always rerun* ligado) |
| Chamada explícita a `st.rerun()` | ✅ Sim |
| Usuário recarrega a página (F5) | ✅ Sim, e **zera** o `session_state` |
| Outro usuário abre o app | ❌ Não afeta sua sessão |
| Passagem do tempo | ❌ Não (é preciso `st.fragment(run_every=...)`) |

:::{important}
Cada aba do navegador é uma **sessão** independente, com seu próprio
`session_state`. Dois usuários no mesmo app não compartilham estado.
:::

### `st.set_page_config`: a primeira linha visual

Configura o título da aba, o ícone, a largura do layout e o estado inicial da
barra lateral.

:::{div}
:class: signature
st.set_page_config(page_title=None, page_icon=None, layout="centered", initial_sidebar_state="auto", menu_items=None)
:::

:::{warning}
`st.set_page_config()` precisa ser **o primeiro comando Streamlit do script**.
Se qualquer `st.` vier antes, o app levanta
`StreamlitAPIException: set_page_config() can only be called once per app page,
and must be called as the first Streamlit command`.
:::

| Argumento | O que faz |
| --- | --- |
| `page_title` | Texto da aba do navegador |
| `page_icon` | Emoji (`"📊"`) ou caminho de imagem |
| `layout` | `"centered"` (padrão) ou `"wide"` — dashboards quase sempre querem `"wide"` |
| `initial_sidebar_state` | `"auto"`, `"expanded"` ou `"collapsed"` |

## Mãos à obra

**Passo 1 — O esqueleto que todo app deveria ter.**

```python
# app.py
import streamlit as st
import pandas as pd

# 1. Configuração da página — SEMPRE o primeiro comando st.
st.set_page_config(
    page_title="Dashboard de Vendas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Carga dos dados (será cacheada no Cap. 11)
df = pd.read_csv("data/vendas.csv", parse_dates=["data"])

# 3. Cabeçalho
st.title("📊 Dashboard de Vendas")
st.caption(f"{len(df):,} registros · {df['data'].min():%b/%Y} a {df['data'].max():%b/%Y}")

# 4. Controles
regiao = st.selectbox("Região", ["Todas"] + sorted(df["regiao"].unique()))

# 5. Transformação
filtrado = df if regiao == "Todas" else df[df["regiao"] == regiao]

# 6. Saída
st.metric("Receita total", f"R$ {filtrado['receita'].sum():,.0f}")
st.bar_chart(filtrado.groupby("categoria")["receita"].sum())
```

Essa ordem — **config → dados → cabeçalho → controles → transformação →
saída** — é a espinha dorsal de todos os apps deste livro.

**Passo 2 — Ver o rerun com os próprios olhos.** O truque é usar um contador que
*sobrevive* ao rerun, para comparar com uma variável que não sobrevive.

```python
import streamlit as st

# sobrevive ao rerun
if "execucoes" not in st.session_state:
    st.session_state.execucoes = 0
st.session_state.execucoes += 1

# NÃO sobrevive ao rerun
contador_local = 0
if st.button("Clique aqui"):
    contador_local += 1

st.metric("Reruns nesta sessão", st.session_state.execucoes)
st.metric("Contador local", contador_local)
st.caption("Clique várias vezes: o primeiro sobe sempre, o segundo nunca passa de 1.")
```

Clique no botão cinco vezes. O contador de reruns chega a 6; o contador local
oscila entre 0 e 1. **Essa é a demonstração mais importante do capítulo.**

**Passo 3 — Interromper cedo com `st.stop`.** Quando uma pré-condição não é
satisfeita, pare o script em vez de aninhar o app inteiro dentro de um `if`.

```python
import streamlit as st
from pathlib import Path

arquivo = Path("data/vendas.csv")

if not arquivo.exists():
    st.error("Dataset não encontrado. Rode `python scripts/gerar_dados.py`.")
    st.stop()          # nada abaixo desta linha é executado

st.success("Dataset carregado.")
# ... o resto do app
```

`st.stop()` encerra o rerun atual imediatamente. É a forma idiomática de tratar
validação de entrada, arquivo ausente ou usuário sem permissão.

:::{card} **Vá além**
O laboratório [`ch03_lab.py`](./labs/ch03_lab.py) combina os três passos e
adiciona um cronômetro que mostra quanto tempo cada rerun leva.
:::

## Questões para reflexão

1. O modelo de rerun torna o código legível de cima para baixo, mas desperdiça
   computação. Em que ponto — quantos usuários, qual tamanho de dado — esse
   desperdício deixa de ser aceitável?
2. Um colega escreve `contador = contador + 1` no topo do app e não entende por
   que o número nunca sobe. Explique o erro dele usando apenas o modelo de
   rerun, sem mencionar `session_state`.
3. `st.set_page_config` precisa ser o primeiro comando. Que restrição técnica do
   navegador ou do protocolo você imagina que justifique isso?
4. Cada aba é uma sessão isolada. Que tipo de funcionalidade de dashboard isso
   torna difícil, e como você contornaria (pense em onde o estado compartilhado
   poderia morar)?
5. `st.stop()` interrompe o rerun. Compare-o com um `return` dentro de uma função
   e com um `raise`: quando cada um é a ferramenta certa em um app Streamlit?

## Teste você mesmo

:::{dropdown} **Q1.** O que acontece, exatamente, quando o usuário arrasta um slider?
**Resposta:** o Streamlit reexecuta o script inteiro do começo. O `st.slider` é
recriado, agora retornando o novo valor, e todo o código posterior roda com esse
valor. A página é então redesenhada com o resultado.
:::

:::{dropdown} **Q2.** Por que uma variável local não consegue acumular valor entre cliques?
**Resposta:** porque ela é recriada do zero a cada rerun. A linha que a inicializa
volta a ser executada, apagando o valor anterior. Para persistir é preciso guardar
em `st.session_state`.
:::

:::{dropdown} **Q3.** Onde `st.set_page_config` deve aparecer, e o que acontece se você errar?
**Resposta:** deve ser o **primeiro comando Streamlit** do script, antes de
qualquer outro `st.`. Caso contrário o app levanta `StreamlitAPIException`.
:::

:::{dropdown} **Q4.** Qual valor de `layout` um dashboard normalmente usa, e por quê?
**Resposta:** `layout="wide"`. O padrão `"centered"` limita o conteúdo a uma
coluna estreita, boa para texto mas ruim para gráficos lado a lado e tabelas
largas.
:::

:::{dropdown} **Q5.** O que `st.stop()` faz, e qual é o caso de uso típico?
**Resposta:** interrompe imediatamente a execução do rerun atual — nada abaixo
dele roda. É usado para validação de pré-condições: arquivo ausente, filtro que
resultou em zero linhas, usuário sem permissão. Evita aninhar o app inteiro
dentro de um `if`.
:::

:::{dropdown} **Q6.** Dois usuários abrem o mesmo app. Eles compartilham o `st.session_state`?
**Resposta:** não. Cada sessão (cada aba de navegador) tem seu próprio
`session_state`, isolado. O que é compartilhado entre sessões é o **cache**
(`st.cache_data` / `st.cache_resource`), assunto do Capítulo 11.
:::

---

:::{div}
:class: chapter-footer
[← Capítulo 2](./ch02-instalacao-e-ambientes.md) · [Índice](../conteudo.md) ·
[Capítulo 4 → `st.write` e os magic commands](../part2/ch04-write-e-magic.md)
:::
