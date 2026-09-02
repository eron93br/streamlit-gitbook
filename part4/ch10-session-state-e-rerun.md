---
title: "10. Session state e o ciclo de rerun"
subject: "Parte 4: Interatividade"
---

# Session state e o ciclo de rerun

:::{admonition} O que você vai aprender
:class: tip
- O que é uma **sessão** e o que sobrevive entre reruns
- Como ler, escrever e inicializar `st.session_state`
- A ligação entre `key` de widget e chave do `session_state`
- Quando usar `st.rerun`, e por que ele raramente é necessário
- `st.fragment` — reexecutar só um pedaço do app
- `st.query_params` — estado que sobrevive ao F5 e é compartilhável por URL
:::

:::{div}
:class: run-quick
**Rode este código:** [`part4/labs/ch10_lab.py`](./labs/ch10_lab.py) — um
contador, um carrinho de compras e um fragmento com auto-atualização.
`streamlit run part4/labs/ch10_lab.py`
:::

:::{div}
:class: api-ref
🔗 **Referência da API:** [Caching and state](https://docs.streamlit.io/develop/api-reference/caching-and-state)
· [`st.session_state`](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state)
:::

## Visão geral

### O problema

Retome o Capítulo 3. A cada interação, o script roda de novo do zero. Logo:

```python
contador = 0
if st.button("+1"):
    contador += 1
st.write(contador)          # nunca passa de 1
```

Variáveis locais são recriadas a cada rerun. Para que algo se acumule, precisa
morar fora do escopo do script.

### `st.session_state`: a memória da sessão

`st.session_state` é um dicionário que **persiste entre reruns da mesma
sessão**. Uma sessão é uma aba do navegador; ela nasce quando o usuário abre o
app e morre quando ele fecha ou recarrega a página.

| | Sobrevive ao rerun? | Sobrevive ao F5? | Compartilhado entre usuários? |
| --- | --- | --- | --- |
| Variável local | ❌ | ❌ | ❌ |
| `st.session_state` | ✅ | ❌ | ❌ |
| `st.query_params` (URL) | ✅ | ✅ | ✅ (via link) |
| `st.cache_data` | ✅ | ✅ | ✅ |

Duas sintaxes equivalentes:

```python
st.session_state["contador"] = 0     # como dicionário
st.session_state.contador = 0        # como atributo
```

### O padrão de inicialização

Como o script roda várias vezes, inicializar sem verificar apagaria o valor a
cada rerun. O idioma correto é:

```python
if "contador" not in st.session_state:
    st.session_state.contador = 0

if st.button("+1"):
    st.session_state.contador += 1

st.metric("Cliques", st.session_state.contador)
```

Alternativa mais compacta:

```python
st.session_state.setdefault("contador", 0)
```

### Widgets e `session_state` são a mesma coisa

Quando você dá um `key` a um widget, o Streamlit cria automaticamente a entrada
correspondente no `session_state`, e as duas ficam sincronizadas.

```python
st.slider("Meta (R$)", 0, 100_000, 50_000, key="meta")

st.write(st.session_state.meta)      # mesmo valor retornado pelo slider
```

Isso permite ler o valor de um widget em qualquer ponto do script, inclusive
**antes** da linha que o desenha (desde que ele já tenha sido criado em um rerun
anterior).

:::{warning}
**A armadilha da atribuição pós-desenho.** Isto levanta exceção:

```python
st.slider("Meta", 0, 100, key="meta")
st.session_state.meta = 0            # ❌ StreamlitAPIException
```

Depois que o widget foi instanciado, seu valor não pode ser alterado no mesmo
rerun. Para resetar, use um **callback** (que roda antes do rerun):

```python
def resetar():
    st.session_state.meta = 0

st.button("Resetar", on_click=resetar)   # ✅
st.slider("Meta", 0, 100, key="meta")
```
:::

### `st.rerun`: force com moderação

`st.rerun()` interrompe a execução atual e reinicia o script imediatamente.

```python
if st.button("Limpar tudo"):
    st.session_state.clear()
    st.rerun()
```

:::{admonition} Quase sempre você não precisa
:class: important
Widgets já disparam rerun sozinhos. `st.rerun()` é para os casos em que você
alterou o estado **depois** do ponto em que ele seria lido e precisa que a página
reflita isso agora. Usado em excesso, produz loops infinitos e piscadas na tela.

Antes de escrever `st.rerun()`, pergunte: *seria mais simples reorganizar a ordem
das linhas?*
:::

### `st.fragment`: rerun parcial

Um decorador que marca uma função como **fragmento**. Interações com widgets
dentro dela reexecutam apenas a função, não o app inteiro.

```python
@st.fragment
def painel_detalhe(df):
    produto = st.selectbox("Produto", sorted(df["produto"].unique()))
    sub = df[df["produto"] == produto]
    st.metric("Receita", f"R$ {sub['receita'].sum():,.0f}")
    st.line_chart(sub.set_index("data")["receita"])

painel_detalhe(filtrado)
```

Trocar de produto agora recalcula só o painel — os KPIs e gráficos do resto da
página ficam intactos. Em dashboards com carga pesada, a diferença é visível.

Com `run_every`, o fragmento se atualiza sozinho:

```python
@st.fragment(run_every="30s")
def status_ao_vivo():
    st.metric("Última leitura", ler_sensor())
```

Esse é o caminho idiomático para dashboards de monitoramento — não use loops
`while True` com `time.sleep`, que bloqueiam a sessão.

### `st.query_params`: estado na URL

`session_state` morre no F5. Para que um recorte seja **compartilhável por
link**, o estado precisa ir para a query string.

```python
# ler
regiao = st.query_params.get("regiao", "Todas")

# escrever
st.query_params["regiao"] = regiao
st.query_params.update({"regiao": regiao, "ano": "2025"})
```

O resultado é uma URL como
`http://localhost:8501/?regiao=Nordeste&ano=2025`, que reabre o dashboard já
filtrado. É o recurso que transforma "veja o dashboard e filtre por Nordeste" em
"clique aqui".

## Mãos à obra

**Passo 1 — Contador: local vs. sessão.**

```python
import streamlit as st

st.session_state.setdefault("cliques", 0)

local = 0
if st.button("Clique"):
    st.session_state.cliques += 1
    local += 1

c1, c2 = st.columns(2)
c1.metric("session_state", st.session_state.cliques)
c2.metric("variável local", local)
```

**Passo 2 — Carrinho: acumulando uma lista.**

```python
st.session_state.setdefault("carrinho", [])

produto = st.selectbox("Produto", ["Notebook Aura", "Fone Pulse", "Monitor Vista"])
qtd = st.number_input("Quantidade", 1, 99, 1)

col1, col2 = st.columns(2)
if col1.button("Adicionar ao carrinho", type="primary"):
    st.session_state.carrinho.append({"produto": produto, "quantidade": qtd})
if col2.button("Esvaziar"):
    st.session_state.carrinho = []

if st.session_state.carrinho:
    st.dataframe(pd.DataFrame(st.session_state.carrinho),
                 use_container_width=True, hide_index=True)
else:
    st.info("Carrinho vazio.")
```

**Passo 3 — Resetar filtros pelo caminho certo.**

```python
def resetar_filtros():
    st.session_state.f_regiao = []
    st.session_state.f_canal = "Todos"

st.sidebar.button("↺ Limpar filtros", on_click=resetar_filtros)

st.sidebar.multiselect("Região", opcoes, key="f_regiao")
st.sidebar.radio("Canal", ["Todos", "E-commerce", "Loja física"], key="f_canal")
```

O callback roda **antes** do rerun, então quando os widgets são desenhados eles
já leem os valores novos. Inverter essa ordem gera exceção.

**Passo 4 — Compartilhar o recorte por URL.**

```python
regioes_disponiveis = sorted(df["regiao"].unique())

# lê o estado inicial da URL
padrao = st.query_params.get_all("regiao") or regioes_disponiveis

selecionadas = st.multiselect("Região", regioes_disponiveis, default=padrao)

# grava de volta na URL
st.query_params["regiao"] = selecionadas

st.caption("Copie a URL do navegador para compartilhar exatamente este recorte.")
```

**Passo 5 — Fragmento com atualização isolada.**

```python
@st.fragment
def detalhe_por_produto(dados):
    p = st.selectbox("Produto", sorted(dados["produto"].unique()), key="frag_prod")
    sub = dados[dados["produto"] == p]
    a, b = st.columns(2)
    a.metric("Receita", f"R$ {sub['receita'].sum():,.0f}")
    b.metric("Unidades", int(sub["unidades"].sum()))
    st.line_chart(sub.set_index("data")["receita"])

detalhe_por_produto(filtrado)
```

:::{card} **Vá além**
O laboratório [`ch10_lab.py`](./labs/ch10_lab.py) traz os cinco passos e um painel
que exibe o conteúdo completo do `session_state` em tempo real — excelente para
depurar.
:::

## Questões para reflexão

1. `session_state` morre no F5 e `query_params` sobrevive. Que tipo de estado
   pertence a cada um? Dê um exemplo de estado que seria **errado** colocar na
   URL.
2. Widgets com `key` sincronizam automaticamente com o `session_state`. Que
   ambiguidade isso cria sobre "quem é o dono" do valor, e como o erro de
   atribuição pós-desenho é consequência disso?
3. `st.rerun()` existe, mas o capítulo recomenda evitá-lo. Descreva um caso em
   que ele é genuinamente a solução mais simples.
4. `st.fragment` melhora o desempenho isolando parte do app. Que classe de bug
   novo esse isolamento introduz (pense em estado compartilhado entre o fragmento
   e o resto)?
5. Cada aba é uma sessão isolada. Se você precisasse de um contador global de
   visitas ao dashboard, onde ele moraria?

## Teste você mesmo

:::{dropdown} **Q1.** O que é uma sessão no Streamlit, e o que a encerra?
**Resposta:** é a conexão de uma aba do navegador com o servidor do app. Ela nasce
quando o usuário abre o app e é encerrada quando ele fecha a aba ou recarrega a
página (F5) — o que zera o `st.session_state`.
:::

:::{dropdown} **Q2.** Escreva o padrão idiomático de inicialização de uma chave no session_state.
**Resposta:**
```python
if "chave" not in st.session_state:
    st.session_state.chave = valor_inicial
```
ou, de forma equivalente, `st.session_state.setdefault("chave", valor_inicial)`.
Inicializar sem verificar apagaria o valor a cada rerun.
:::

:::{dropdown} **Q3.** Por que atribuir a `st.session_state.x` depois de desenhar um widget com `key="x"` levanta exceção?
**Resposta:** porque, uma vez instanciado no rerun atual, o widget é o dono do
valor daquela chave e ele não pode ser sobrescrito no mesmo ciclo. A forma
correta de alterar é em um **callback** (`on_click` / `on_change`), que executa
antes do rerun em que o widget será redesenhado.
:::

:::{dropdown} **Q4.** O que `st.fragment` faz?
**Resposta:** marca uma função de modo que interações com widgets dentro dela
reexecutem apenas aquela função, e não o script inteiro. Com o argumento
`run_every` ela também se reexecuta periodicamente, sozinha.
:::

:::{dropdown} **Q5.** Qual a diferença prática entre guardar um filtro em `session_state` e guardá-lo em `query_params`?
**Resposta:** o `session_state` é volátil e privado da aba — some no F5 e não pode
ser compartilhado. O `query_params` grava o estado na URL, então sobrevive ao
recarregamento e permite compartilhar o recorte exato por link.
:::

:::{dropdown} **Q6.** Como implementar corretamente um botão "limpar filtros"?
**Resposta:** com um callback que altera as chaves antes do rerun:
```python
def limpar():
    st.session_state.f_regiao = []

st.button("Limpar", on_click=limpar)
st.multiselect("Região", opcoes, key="f_regiao")
```
:::

---

:::{div}
:class: chapter-footer
[← Capítulo 9](./ch09-widgets-de-input.md) · [Índice](../conteudo.md) ·
[Capítulo 11 → Cache e performance](./ch11-cache-e-performance.md)
:::
