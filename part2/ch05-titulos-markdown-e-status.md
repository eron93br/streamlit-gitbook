---
title: "5. Títulos, markdown e mensagens de status"
subject: "Parte 2: Elementos de Texto"
---

# Títulos, markdown e mensagens de status

:::{admonition} O que você vai aprender
:class: tip
- A hierarquia de títulos: `st.title`, `st.header`, `st.subheader`, `st.caption`
- O markdown estendido do Streamlit: cores, emojis, badges, LaTeX
- Quando usar `st.text`, `st.code`, `st.latex` e `st.divider`
- As cinco mensagens de status — `success`, `info`, `warning`, `error`, `exception`
- Indicadores de progresso: `st.progress`, `st.spinner`, `st.status`, `st.toast`
:::

:::{div}
:class: run-quick
**Rode este código:** [`part2/labs/ch05_lab.py`](./labs/ch05_lab.py) — uma
galeria de todos os elementos de texto e status.
`streamlit run part2/labs/ch05_lab.py`
:::

:::{div}
:class: api-ref
🔗 **Referência da API:** [Text elements](https://docs.streamlit.io/develop/api-reference/text)
· [Status elements](https://docs.streamlit.io/develop/api-reference/status)
:::

## Visão geral

### A hierarquia de títulos

Um dashboard sem hierarquia visual é uma parede de gráficos. As funções de
título dão estrutura à leitura — e, no Streamlit, também alimentam o índice
lateral automático de cada página.

| Função | Equivalente HTML | Uso típico |
| --- | --- | --- |
| `st.title` | `<h1>` | O nome do dashboard. **Um por página.** |
| `st.header` | `<h2>` | Seções principais ("Visão geral", "Detalhamento") |
| `st.subheader` | `<h3>` | Subseções dentro de uma seção |
| `st.caption` | texto pequeno e cinza | Nota de rodapé, fonte do dado, data de atualização |
| `st.markdown` | livre | Qualquer coisa; o canivete suíço |
| `st.text` | `<pre>` | Texto monoespaçado **sem** interpretar markdown |
| `st.divider` | `<hr>` | Linha horizontal separando blocos |

```python
st.title("📊 Dashboard de Vendas")
st.caption("Dados sintéticos · atualizado em 02/09/2026")
st.divider()

st.header("Visão geral")
st.subheader("Receita por região")
```

Todas as funções de título aceitam `anchor=` (para links diretos) e `help=`
(para um ícone de ajuda com tooltip).

### O markdown estendido do Streamlit

`st.markdown` aceita CommonMark, e o Streamlit acrescenta três extensões que
aparecem o tempo todo em dashboards.

**1. Cores no texto** — sintaxe `:cor[texto]`.

```python
st.markdown("Meta: :green[atingida] · Risco: :red[alto] · Nota: :blue[revisar]")
```

Cores disponíveis: `blue`, `green`, `orange`, `red`, `violet`, `gray`/`grey`,
`rainbow`, `primary`. Há também fundos coloridos com `:green-background[texto]`.

**2. Emojis por atalho** — `:sunglasses:`, `:chart_with_upwards_trend:`,
`:warning:`. A lista completa está no
[emoji cheat sheet](https://share.streamlit.io/streamlit/emoji-shortcodes).

**3. LaTeX inline e em bloco** — útil para explicitar a fórmula de uma métrica.

```python
st.markdown("A margem é $m = \\frac{lucro}{receita}$.")
st.latex(r"\text{ticket médio} = \frac{\sum \text{receita}}{\#\text{pedidos}}")
```

:::{admonition} Markdown em (quase) todo lugar
:class: tip
A sintaxe de cor e emoji funciona também em `st.title`, `st.header`,
`st.subheader`, `st.caption`, nos rótulos de widgets (`label=`) e nos textos de
`st.success`/`st.info`/`st.warning`/`st.error`. Um rótulo de slider pode ser
`"Receita mínima :gray[(em milhares)]"`.
:::

### Texto literal e código

```python
st.text("Isto **não** vira negrito.\n   E os espaços são preservados.")

st.code(
    """
    df.groupby("regiao")["receita"].sum()
    """,
    language="python",
    line_numbers=True,
)
```

`st.code` é a forma correta de mostrar código: destaque de sintaxe, botão de
cópia e numeração opcional de linhas. `st.echo` faz o inverso — executa um bloco
**e** o exibe, útil para material didático.

### Badges

`st.badge` cria um selo colorido compacto, ótimo para indicar status de um KPI
sem gastar uma linha inteira.

```python
st.badge("Em dia", color="green")
st.badge("Atenção", color="orange", icon=":material/warning:")
```

Você também consegue o mesmo efeito dentro de markdown com a sintaxe
`:green-badge[Em dia]`.

### As cinco mensagens de status

| Função | Cor | Quando usar |
| --- | --- | --- |
| `st.success` | verde | Operação concluída, meta atingida |
| `st.info` | azul | Contexto neutro, dica de uso |
| `st.warning` | amarelo | Dado incompleto, filtro muito restritivo |
| `st.error` | vermelho | Falha que impede o app de continuar |
| `st.exception` | vermelho | Traceback completo — só em modo de desenvolvimento |

```python
if filtrado.empty:
    st.warning("Nenhum registro para os filtros selecionados. Amplie o período.")
    st.stop()

st.success(f"{len(filtrado):,} registros carregados.")
```

:::{warning}
`st.exception(e)` imprime o traceback completo na tela. É excelente para
depurar e **inadequado para produção**: expõe caminhos de arquivo e detalhes
internos ao usuário final. Em produção, prefira `st.error` com uma mensagem
tratada e registre o traceback em log.
:::

### Progresso e espera

| Função | Forma | Uso |
| --- | --- | --- |
| `st.spinner` | context manager | Operação curta e indeterminada |
| `st.progress` | barra 0–100 | Loop com número de passos conhecido |
| `st.status` | container expansível | Processo de várias etapas com log |
| `st.toast` | notificação flutuante | Confirmação discreta, não bloqueante |
| `st.balloons` / `st.snow` | animação | Celebração — use com parcimônia |

```python
with st.spinner("Carregando dados…"):
    df = carregar()

barra = st.progress(0, text="Processando regiões")
for i, regiao in enumerate(regioes, start=1):
    processar(regiao)
    barra.progress(i / len(regioes), text=f"Processando {regiao}")
barra.empty()

with st.status("Executando pipeline", expanded=True) as s:
    st.write("Lendo CSV…")
    st.write("Agregando por categoria…")
    s.update(label="Pipeline concluído", state="complete", expanded=False)

st.toast("Relatório exportado", icon="✅")
```

## Mãos à obra

**Passo 1 — Um cabeçalho de dashboard completo.**

```python
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Vendas", page_icon="📊", layout="wide")

df = pd.read_csv("data/vendas.csv", parse_dates=["data"])

st.title("📊 Dashboard de Vendas")
st.caption(
    f"Fonte: dados sintéticos · {len(df):,} registros · "
    f"período {df['data'].min():%d/%m/%Y} a {df['data'].max():%d/%m/%Y}"
)
st.divider()
```

**Passo 2 — Semaforizar um indicador com markdown colorido.**

```python
meta = 4_000_000
receita = df["receita"].sum()
atingimento = receita / meta

if atingimento >= 1:
    st.markdown(f"### Receita: :green[R$ {receita:,.0f}] :white_check_mark:")
    st.success(f"Meta superada em {atingimento - 1:.1%}.")
elif atingimento >= 0.9:
    st.markdown(f"### Receita: :orange[R$ {receita:,.0f}] :warning:")
    st.warning(f"Faltam {1 - atingimento:.1%} para a meta.")
else:
    st.markdown(f"### Receita: :red[R$ {receita:,.0f}] :arrow_down:")
    st.error(f"Abaixo da meta em {1 - atingimento:.1%}.")
```

Note o padrão: a **cor no texto** comunica o estado e a **mensagem de status**
explica o porquê. Um sem o outro é decoração ou parede de texto.

**Passo 3 — Documentar a fórmula da métrica.** Dashboards ganham credibilidade
quando explicitam como cada número é calculado.

```python
with st.expander("Como calculamos a margem"):
    st.latex(r"\text{margem} = \frac{\text{receita} - \text{custo}}{\text{receita}}")
    st.code(
        'df["margem"] = (df["receita"] - df["custo"]) / df["receita"]',
        language="python",
    )
    st.caption("Custos indiretos não estão incluídos.")
```

**Passo 4 — Feedback de processo longo.**

```python
import time

with st.status("Atualizando base", expanded=True) as status:
    st.write("Conectando à fonte…")
    time.sleep(0.6)
    st.write("Baixando registros…")
    time.sleep(0.9)
    st.write("Validando esquema…")
    time.sleep(0.4)
    status.update(label="Base atualizada", state="complete", expanded=False)

st.toast("Pronto!", icon="🎉")
```

:::{card} **Vá além**
O laboratório [`ch05_lab.py`](./labs/ch05_lab.py) é uma galeria navegável de
todos os elementos deste capítulo, com o código de cada um visível ao lado.
:::

## Questões para reflexão

1. `st.title`, `st.header` e `st.markdown("# ...")` podem produzir resultados
   visualmente parecidos. Que argumento a favor das funções semânticas você daria
   a alguém que só se importa com a aparência?
2. A sintaxe `:red[texto]` facilita colorir números. Que risco de acessibilidade
   isso cria, e como você o mitigaria sem abrir mão da cor?
3. `st.exception` é ótimo em desenvolvimento e perigoso em produção. Como você
   estruturaria o app para trocar automaticamente entre os dois comportamentos?
4. Um app usa `st.balloons()` a cada filtro aplicado. Além do exagero estético,
   que problema de comunicação isso cria para o usuário frequente?
5. `st.status` mostra o progresso de um pipeline em etapas. Em que medida
   mostrar o processo aumenta — ou diminui — a confiança do usuário no resultado?

## Teste você mesmo

:::{dropdown} **Q1.** Qual a diferença entre `st.text` e `st.markdown`?
**Resposta:** `st.text` exibe texto literal em fonte monoespaçada, preservando
espaços e **sem** interpretar markdown. `st.markdown` interpreta a sintaxe
markdown (negrito, listas, links) mais as extensões do Streamlit (cores, emojis,
LaTeX).
:::

:::{dropdown} **Q2.** Como escrever a palavra "crítico" em vermelho dentro de um título?
**Resposta:** usando a sintaxe de cor do markdown estendido, que funciona também
nas funções de título: `st.subheader("Status: :red[crítico]")`.
:::

:::{dropdown} **Q3.** Quando usar `st.spinner` em vez de `st.progress`?
**Resposta:** `st.spinner` quando a operação é indeterminada — você não sabe
quantos passos faltam nem quanto tempo levará. `st.progress` quando há um número
conhecido de iterações e é possível informar a fração concluída.
:::

:::{dropdown} **Q4.** Qual função exibe código Python com destaque de sintaxe e botão de cópia?
**Resposta:** `st.code(texto, language="python")`. O parâmetro `line_numbers=True`
adiciona numeração de linhas.
:::

:::{dropdown} **Q5.** Por que evitar `st.exception` em produção?
**Resposta:** ela imprime o traceback completo na interface, expondo caminhos de
arquivo, nomes de variáveis e estrutura interna do sistema ao usuário final — um
risco de segurança e uma péssima experiência. Em produção prefira `st.error` com
mensagem tratada, registrando o traceback em log.
:::

:::{dropdown} **Q6.** O que `st.status` oferece que `st.spinner` não oferece?
**Resposta:** um container expansível que acumula o log das etapas conforme elas
acontecem, e cujo rótulo e estado (`running`, `complete`, `error`) podem ser
atualizados via `status.update(...)`. É adequado a processos de múltiplas etapas.
:::

---

:::{div}
:class: chapter-footer
[← Capítulo 4](./ch04-write-e-magic.md) · [Índice](../conteudo.md) ·
[Capítulo 6 → Plotly Express](../part3/ch06-plotly-express.md)
:::
