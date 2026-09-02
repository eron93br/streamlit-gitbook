---
title: "12. Layouts e containers"
subject: "Parte 5: Layout e Estrutura"
---

# Layouts e containers

:::{admonition} O que você vai aprender
:class: tip
- As duas sintaxes de container: `with bloco:` e `bloco.metodo()`
- `st.columns` — a base de qualquer grade de dashboard
- `st.tabs`, `st.expander`, `st.popover` e `st.container`
- A barra lateral (`st.sidebar`) e a convenção filtro/resultado
- `st.empty` — reservar um lugar na tela e preenchê-lo depois
- `st.dialog` — janelas modais
- Como desenhar um dashboard de verdade: a grade F
:::

:::{div}
:class: run-quick
**Rode este código:** [`part5/labs/ch12_lab.py`](./labs/ch12_lab.py) — o mesmo
conteúdo em quatro layouts diferentes, para comparar.
`streamlit run part5/labs/ch12_lab.py`
:::

:::{div}
:class: api-ref
🔗 **Referência da API:** [Layouts and containers](https://docs.streamlit.io/develop/api-reference/layout)
:::

## Visão geral

### O problema

O Streamlit empilha elementos verticalmente, na ordem do script. Isso é ótimo
para narrativa e péssimo para dashboards: quatro KPIs empilhados ocupam uma tela
inteira e obrigam a rolagem para ver o primeiro gráfico.

Os **containers** quebram o empilhamento e organizam a tela em duas dimensões.

### Duas sintaxes, o mesmo efeito

Todo container aceita ser usado das duas formas:

```python
# 1. Como context manager — melhor quando há vários elementos
col1, col2 = st.columns(2)
with col1:
    st.metric("Receita", "R$ 9,7 mi")
    st.caption("Acumulado 2025")

# 2. Como objeto com métodos — melhor para um elemento só
col2.metric("Lucro", "R$ 3,1 mi")
```

A primeira é mais legível quando o bloco tem várias linhas; a segunda é mais
concisa para um elemento isolado.

### `st.columns`

:::{div}
:class: signature
st.columns(spec, gap="small", vertical_alignment="top", border=False)
:::

```python
a, b, c = st.columns(3)                       # três colunas iguais
esq, dir = st.columns([2, 1])                 # a esquerda tem o dobro da largura
p, q = st.columns(2, gap="large", border=True)
```

| Argumento | Efeito |
| --- | --- |
| `spec` | Número de colunas, ou lista de pesos relativos (`[3, 1]`) |
| `gap` | `"small"`, `"medium"`, `"large"` — o espaçamento entre elas |
| `vertical_alignment` | `"top"`, `"center"`, `"bottom"` — alinha conteúdos de alturas diferentes |
| `border` | Desenha uma borda em cada coluna |

:::{admonition} Colunas aninhadas
:class: warning
Colunas podem ser aninhadas **um nível** na área principal (uma coluna dentro de
uma coluna). Dentro da sidebar, não é permitido aninhar. Se você precisa de mais
níveis, o layout provavelmente está complexo demais — reconsidere.
:::

### `st.tabs`

Abas escondem conteúdo até que ele seja pedido. Perfeitas para visões
alternativas do mesmo recorte.

```python
aba1, aba2, aba3 = st.tabs(["📈 Evolução", "🗺️ Regiões", "📋 Dados"])

with aba1:
    st.plotly_chart(fig_linha, use_container_width=True)
with aba2:
    st.plotly_chart(fig_mapa, use_container_width=True)
with aba3:
    st.dataframe(filtrado, use_container_width=True)
```

:::{important}
O conteúdo de **todas** as abas é executado a cada rerun, mesmo o das abas
fechadas — o Streamlit só esconde visualmente. Se cada aba faz um cálculo pesado,
o custo é a soma de todas. Combine com `st.cache_data` ou `st.fragment`.
:::

### `st.expander` e `st.popover`

| | Ocupa espaço fechado? | Uso típico |
| --- | --- | --- |
| `st.expander` | Sim (uma linha de título) | Metodologia, filtros avançados, tabela de apoio |
| `st.popover` | Não (é um botão) | Ajuda contextual, mini-formulário, ações secundárias |

```python
with st.expander("ℹ️ Como calculamos a margem"):
    st.latex(r"\text{margem} = \frac{\text{receita} - \text{custo}}{\text{receita}}")

with st.popover("⚙️ Opções"):
    suavizar = st.checkbox("Suavizar série")
    janela = st.slider("Janela (meses)", 1, 12, 3)
```

### `st.container`

Um agrupador genérico. Serve para (a) dar borda/altura a um bloco e (b)
"reservar" um lugar no fluxo e escrever nele depois.

```python
cartao = st.container(border=True, height=260)
with cartao:
    st.subheader("Top 5 produtos")
    st.dataframe(top5, hide_index=True, use_container_width=True)
```

O argumento `height` cria uma área de rolagem interna — útil para listas longas
que não devem alongar a página.

### `st.empty`: o placeholder

`st.empty()` cria um espaço vazio que pode ser **substituído** depois. Ele guarda
apenas um elemento por vez: escrever de novo sobrescreve o anterior.

```python
placeholder = st.empty()

for i in range(1, 6):
    placeholder.metric("Processando", f"{i}/5")
    time.sleep(0.4)

placeholder.success("Concluído!")     # substitui a métrica
```

É também a solução para o problema de ordem: exibir no topo da página um valor
que só é calculado no final do script.

### `st.sidebar`

A barra lateral é um container como os outros — tudo que vai na página principal
pode ir nela.

```python
with st.sidebar:
    st.header("Filtros")
    regiao = st.multiselect("Região", opcoes)
    st.divider()
    st.caption("Atualizado em 02/09/2026")
```

:::{admonition} A convenção
:class: tip
**Sidebar = controles. Área principal = resultados.**

Usuários de dashboards aprenderam essa gramática com o Power BI, o Tableau e o
Looker. Quebrá-la sem motivo custa alguns segundos de confusão a cada novo
usuário.
:::

### `st.dialog`: janelas modais

```python
@st.dialog("Detalhes do pedido")
def detalhe(pedido):
    st.write(f"**Produto:** {pedido['produto']}")
    st.metric("Receita", f"R$ {pedido['receita']:,.2f}")
    if st.button("Fechar"):
        st.rerun()

if st.button("Ver detalhes"):
    detalhe(linha_selecionada)
```

Modais interrompem o fluxo — use para confirmação de ação destrutiva ou detalhe
sob demanda, nunca para conteúdo principal.

### A grade de um dashboard

Olhos ocidentais varrem a tela em **F**: a linha superior inteira, depois a
coluna esquerda, com atenção decrescente. O layout padrão que respeita isso:

```text
┌──────────────────────────────────────────────────┐
│  Título · legenda · período                      │  ← contexto
├──────────┬──────────┬──────────┬─────────────────┤
│  KPI 1   │  KPI 2   │  KPI 3   │  KPI 4          │  ← o quê (números)
├──────────┴──────────┴──┬───────┴─────────────────┤
│  Gráfico principal     │  Gráfico de apoio       │  ← por quê (tendência)
│  (série temporal)      │  (composição)           │
├────────────────────────┴─────────────────────────┤
│  Tabela detalhada (expander ou aba)              │  ← detalhe sob demanda
└──────────────────────────────────────────────────┘
```

- **Números grandes no topo**: respondem "estamos bem?" em dois segundos.
- **Tendência à esquerda, composição à direita**: a série temporal é a pergunta
  mais frequente.
- **Detalhe embaixo ou escondido**: quem precisa procura.

## Mãos à obra

**Passo 1 — Linha de KPIs.**

```python
st.set_page_config(layout="wide")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Receita", "R$ 9,7 mi", "+12,4%", border=True)
k2.metric("Lucro", "R$ 3,1 mi", "+8,1%", border=True)
k3.metric("Ticket médio", "R$ 812", "-2,3%", border=True)
k4.metric("Satisfação", "4,1 / 5", "+0,1", border=True)
```

**Passo 2 — Grade principal 2:1.**

```python
esq, dir = st.columns([2, 1], gap="large")

with esq:
    st.subheader("Evolução mensal")
    st.plotly_chart(fig_linha, use_container_width=True)

with dir:
    st.subheader("Composição")
    st.plotly_chart(fig_pizza, use_container_width=True)
```

**Passo 3 — Abas para as visões alternativas.**

```python
aba_reg, aba_cat, aba_dados = st.tabs(["Por região", "Por categoria", "Dados"])

with aba_reg:
    st.plotly_chart(fig_regiao, use_container_width=True)
with aba_cat:
    st.plotly_chart(fig_categoria, use_container_width=True)
with aba_dados:
    st.dataframe(filtrado.head(500), use_container_width=True, hide_index=True)
    st.download_button("⬇️ CSV completo",
                       filtrado.to_csv(index=False).encode("utf-8-sig"),
                       "dados.csv", "text/csv")
```

**Passo 4 — Metodologia em um expander.**

```python
with st.expander("📖 Metodologia e definições"):
    st.markdown("""
    - **Receita**: soma de `unidades × preço unitário`.
    - **Lucro**: receita menos custo direto. Não inclui despesas indiretas.
    - **Ticket médio**: receita dividida pelo número de pedidos.
    """)
    st.caption("Dados sintéticos, gerados por `scripts/gerar_dados.py`.")
```

**Passo 5 — Placeholder para um valor calculado no fim.**

```python
resumo_topo = st.empty()          # reserva o lugar

# ... 200 linhas de processamento ...

resumo_topo.info(
    f"Analisando {len(filtrado):,} registros · "
    f"receita de R$ {filtrado['receita'].sum():,.0f}"
)
```

:::{card} **Vá além**
O laboratório [`ch12_lab.py`](./labs/ch12_lab.py) mostra o mesmo conjunto de
elementos em quatro arranjos (empilhado, colunas, abas e grade completa) para você
sentir a diferença.
:::

## Questões para reflexão

1. A grade F privilegia o topo e a esquerda. Que tipo de informação você
   deliberadamente colocaria no canto inferior direito, e por quê?
2. Abas escondem conteúdo mas executam tudo. Que problema de desempenho isso
   cria, e em que ponto você trocaria abas por navegação multipágina?
3. A convenção "sidebar = filtros" é forte. Descreva um dashboard em que
   quebrá-la seria a decisão certa.
4. `st.expander` esconde a metodologia. Isso protege o layout ou esconde
   informação essencial? Como você decidiria caso a caso?
5. Um layout com muitas colunas fica ilegível no celular. Que estratégia você
   adotaria, sabendo que o Streamlit empilha colunas automaticamente em telas
   estreitas?

## Teste você mesmo

:::{dropdown} **Q1.** Quais são as duas sintaxes para escrever dentro de um container?
**Resposta:** como context manager (`with col1: st.metric(...)`) ou chamando o
método diretamente no objeto (`col1.metric(...)`). A primeira é mais legível para
blocos com várias linhas.
:::

:::{dropdown} **Q2.** Como criar duas colunas em que a primeira tem o triplo da largura da segunda?
**Resposta:** passando uma lista de pesos: `esq, dir = st.columns([3, 1])`.
:::

:::{dropdown} **Q3.** O conteúdo de uma aba fechada é executado?
**Resposta:** sim. O Streamlit executa o código de todas as abas a cada rerun e
apenas esconde visualmente as não selecionadas. Cálculos pesados em várias abas
somam custo — combine com cache ou fragmentos.
:::

:::{dropdown} **Q4.** Qual a diferença entre `st.expander` e `st.popover`?
**Resposta:** o `expander` ocupa espaço permanente no fluxo (uma linha de título
que se abre para baixo); o `popover` é um botão que abre um painel flutuante,
sem consumir espaço quando fechado. Expander para conteúdo de apoio; popover para
ações e ajuda contextual.
:::

:::{dropdown} **Q5.** Para que serve `st.empty()`?
**Resposta:** reserva um lugar no fluxo da página que pode ser preenchido — e
substituído — depois. Guarda um elemento por vez. Serve para atualizar um valor
em loop e para exibir no topo algo calculado no fim do script.
:::

:::{dropdown} **Q6.** Qual a convenção de layout para filtros e resultados, e por que segui-la?
**Resposta:** filtros na barra lateral (`st.sidebar`), resultados na área
principal. É a gramática que os usuários já conhecem de outras ferramentas de BI;
quebrá-la sem motivo impõe custo de aprendizado desnecessário.
:::

---

:::{div}
:class: chapter-footer
[← Capítulo 11](../part4/ch11-cache-e-performance.md) · [Índice](../conteudo.md) ·
[Capítulo 13 → Apps multipágina e navegação](./ch13-multipage-e-navegacao.md)
:::
