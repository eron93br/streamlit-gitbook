---
title: "15. Roteiro de construção de um dashboard"
subject: "Parte 6: Construindo o Dashboard"
---

# Roteiro de construção de um dashboard

:::{admonition} O que você vai aprender
:class: tip
- As três etapas antes de escrever a primeira linha de código
- Como definir o **tipo** do dashboard e as métricas que ele responde
- Por que a AED vem antes do dashboard, e o que procurar nela
- Como desenhar um wireframe em papel — e por que isso economiza horas
- A pergunta de governança: **todos os usuários podem ver todos os dados?**
- Um checklist de entrega
:::

:::{div}
:class: run-quick
**Este capítulo não tem app.** Ele é a etapa de projeto. O resultado dele é o
insumo do [Capítulo 16](./ch16-projeto-guiado.md), onde construímos o dashboard.
:::

:::{div}
:class: api-ref
🔗 **Leitura recomendada:** [Crafting a dashboard app in Python using Streamlit](https://blog.streamlit.io/crafting-a-dashboard-app-in-python-using-streamlit/) (blog oficial)
:::

## Visão geral

### As três etapas

> **Sempre imagine o dashboard antes de construí-lo — ou seja: desenhe antes de
> codar.**

O roteiro é curto e a ordem importa:

```text
1. Definir as métricas e o tipo do dashboard      ← papel e conversa
2. Realizar a Análise Exploratória de Dados       ← notebook
3. Seguir os passos de construção no Streamlit    ← código
```

A tentação é começar no passo 3. Quem começa no passo 3 constrói um dashboard
bonito que ninguém usa, porque ele responde às perguntas erradas — ou porque os
dados não sustentam as perguntas certas.

### Etapa 1 · Definir as métricas e o tipo

**Comece pela decisão, não pelo dado.** A pergunta fundadora é sempre:

> *Que decisão essa pessoa vai tomar depois de olhar esta tela?*

Se não houver resposta, você está construindo um relatório, não um dashboard —
e relatórios são mais bem servidos por um PDF.

**Os quatro tipos de dashboard**

| Tipo | Pergunta que responde | Horizonte | Exemplo |
| --- | --- | --- | --- |
| **Estratégico** | Estamos indo bem? | Trimestre / ano | Receita vs. meta anual por região |
| **Analítico** | Por que isso aconteceu? | Mês / trimestre | Decomposição da queda de margem |
| **Operacional** | O que está acontecendo agora? | Hoje / tempo real | Pedidos em atraso, fila de atendimento |
| **Tático** | Como estamos executando o plano? | Semana / mês | Progresso das iniciativas por time |

O tipo determina quase tudo: frequência de atualização, nível de agregação,
quantidade de filtros e até a paleta. Um dashboard estratégico com trinta filtros
falhou; um operacional com atualização mensal também.

**Escolher as métricas**

Um bom conjunto de KPIs tem entre **três e cinco** métricas e satisfaz:

1. **Acionável** — mudar o número está no alcance de quem olha.
2. **Comparável** — existe uma referência (meta, período anterior, média).
3. **Inequívoca** — duas pessoas calculam o mesmo número da mesma forma.
4. **Estável** — a definição não muda a cada reunião.

:::{admonition} Escreva o dicionário de métricas
:class: important
Antes de codar, escreva em uma tabela: **nome, fórmula, fonte, granularidade,
dono**. Metade das discussões sobre "o número está errado" é, na verdade, uma
divergência de definição.

| Métrica | Fórmula | Fonte | Grão | Dono |
| --- | --- | --- | --- | --- |
| Receita | Σ `unidades × preço_unitário` | `vendas.csv` | pedido | Comercial |
| Margem | (receita − custo) / receita | `vendas.csv` | pedido | Financeiro |
| Ticket médio | receita / nº de pedidos | derivado | dia | Comercial |
:::

### Etapa 2 · Realizar a AED

A Análise Exploratória de Dados não é uma formalidade acadêmica antes do
dashboard — ela é o que **impede** que o dashboard minta. O que procurar:

| Verificação | Por que importa para o dashboard |
| --- | --- |
| Valores ausentes | Um `NaN` em `receita` faz a soma mentir silenciosamente |
| Tipos das colunas | Data como string quebra qualquer agrupamento temporal |
| Duplicatas | Inflam totais sem qualquer aviso |
| Outliers | Um pedido de R$ 2 milhões domina a escala de todos os gráficos |
| Cardinalidade | Uma coluna com 4.000 valores distintos não cabe em um `selectbox` |
| Cobertura temporal | Lacunas viram quedas falsas na série |
| Distribuições | Definem se a escala deve ser linear ou logarítmica |
| Correlações | Sugerem quais cruzamentos valem um gráfico |

O produto da AED é duplo: uma **decisão de limpeza** (documentada) e uma
**lista curta de gráficos** que valem a pena.

:::{admonition} O que a AED entrega ao dashboard
:class: tip
1. Um DataFrame limpo, com tipos corretos e regras de tratamento documentadas.
2. Os 4 a 6 gráficos que efetivamente comunicam algo — já testados no notebook,
   como manda o [Capítulo 6](../part3/ch06-plotly-express.md).
3. As faixas realistas dos filtros (períodos, valores mínimos e máximos).
:::

### Etapa 3 · Desenhar antes de codar

Um wireframe em papel leva dez minutos e evita horas de reorganização de
`st.columns`. Não precisa ser bonito:

```text
┌──────────────────────────────────────────────────────┐
│  📊 Dashboard de Vendas          [período] [região]  │
├────────────┬────────────┬────────────┬───────────────┤
│  RECEITA   │   LUCRO    │  TICKET    │  SATISFAÇÃO   │
│  R$ 9,7mi  │  R$ 3,1mi  │   R$ 812   │    4,1/5      │
│  ▲ 12,4%   │  ▲ 8,1%    │   ▼ 2,3%   │    — 0,0      │
├────────────┴────────────┴──┬─────────┴───────────────┤
│  Evolução mensal           │  Receita por categoria  │
│  (linha: receita e lucro)  │  (barras horizontais)   │
├────────────────────────────┴─────────────────────────┤
│  ▸ Detalhamento (tabela + download)                  │
└──────────────────────────────────────────────────────┘
   [sidebar: região, categoria, canal, período, ticket]
```

Ao desenhar, decida três coisas:

1. **O que aparece sem rolagem** (a *dobra*) — é isso que 80% dos usuários verão.
2. **O que é filtro e o que é resultado** — filtros na sidebar, resultados no
   corpo.
3. **O que fica escondido** — detalhe em expander ou aba, não na tela principal.

### A pergunta de governança

:::{admonition} Todos os usuários PODEM acessar todos os dados?
:class: important
Essa pergunta apareceu na aula e merece um lugar de destaque no roteiro. Um
dashboard corporativo típico cruza dados de naturezas muito diferentes:

| Domínio | Sensibilidade | Quem deveria ver |
| --- | --- | --- |
| **Financeiro** | Alta — margem, custo, resultado por cliente | Diretoria, controladoria |
| **Estoque (insumos)** | Média — custo unitário, fornecedores | Operação, compras |
| **Estratégia de apoio aos funcionários** | Alta — dados de pessoas | RH, gestores diretos |
| **Cultura** | Média — pesquisas de clima | RH, liderança (agregado) |

Antes de publicar, responda:

1. **Quem** vai acessar? (papéis, não pessoas)
2. **Qual recorte** cada papel pode ver? (linhas e colunas)
3. **O agregado é seguro?** Uma média de satisfação de um time de três pessoas
   pode identificar indivíduos.
4. **O download é permitido?** Um `st.download_button` é uma porta de saída de
   dados.
5. **Onde está a verificação?** Esconder a página do menu não é controle de
   acesso — a checagem precisa estar antes do carregamento do dado
   ([Capítulo 13](../part5/ch13-multipage-e-navegacao.md)).
:::

## Mãos à obra

Aplique o roteiro ao dataset do livro. O resultado será construído no
[Capítulo 16](./ch16-projeto-guiado.md).

**Passo 1 — Ficha do dashboard.** Preencha (em um documento, não no código):

```text
Nome:        Dashboard de Vendas 2024–2025
Tipo:        Analítico
Público:     Gerência comercial (5 pessoas)
Decisão:     Onde realocar o esforço comercial no próximo trimestre
Frequência:  Atualização mensal
Restrições:  Custo e margem visíveis apenas para a gerência
```

**Passo 2 — Dicionário de métricas.**

| Métrica | Fórmula | Meta | Direção |
| --- | --- | --- | --- |
| Receita | Σ `receita` | R$ 5 mi/ano | ↑ bom |
| Lucro | Σ `lucro` | R$ 1,6 mi/ano | ↑ bom |
| Margem | Σ lucro / Σ receita | ≥ 32% | ↑ bom |
| Ticket médio | Σ receita / nº pedidos | R$ 800 | ↑ bom |
| Custo | Σ `custo` | — | ↓ bom |

A coluna **direção** determina o `delta_color` de cada `st.metric`
([Capítulo 7](../part3/ch07-exibindo-dados.md)).

**Passo 3 — AED mínima, no notebook.**

```python
import pandas as pd

df = pd.read_csv("data/vendas.csv", parse_dates=["data"])

df.info()
df.describe()
df.isna().sum()                               # satisfacao tem ~1,5% de nulos
df.duplicated().sum()
df["data"].dt.to_period("M").value_counts().sort_index()   # cobertura temporal
df.select_dtypes("number").corr()

for col in ["regiao", "categoria", "canal", "produto"]:
    print(col, df[col].nunique())             # cardinalidade → cabe em selectbox?
```

Decisões documentadas para este dataset:

- `satisfacao` tem ~1,5% de nulos → manter como `NaN` e usar `mean()`, que os
  ignora; sinalizar a cobertura no rodapé do gráfico.
- `produto` tem 20 valores distintos → cabe em `multiselect`.
- Sem duplicatas; cobertura temporal completa nos 24 meses.

**Passo 4 — Lista de gráficos.** Da AED, saem quatro que valem a tela:

| # | Gráfico | Responde |
| --- | --- | --- |
| 1 | Linha: receita e lucro por mês | Estamos crescendo? Há sazonalidade? |
| 2 | Barras horizontais: receita por categoria e canal | Onde está o volume? |
| 3 | Dispersão: unidades × receita por produto | Que produtos carregam o resultado? |
| 4 | Heatmap: região × categoria | Onde há espaço para crescer? |

**Passo 5 — Wireframe.** Desenhe em papel. Sério. Fotografe e coloque no
repositório — é documentação de projeto.

**Passo 6 — Checklist de entrega.**

- [ ] O dashboard responde à pergunta da ficha em menos de 10 segundos?
- [ ] Todos os números têm unidade e período explícitos?
- [ ] Existe estado vazio tratado (filtro sem resultado)?
- [ ] A metodologia está documentada no próprio app (expander)?
- [ ] A data da última atualização aparece na tela?
- [ ] Os filtros têm valores padrão sensatos?
- [ ] O app carrega em menos de 3 segundos (com cache)?
- [ ] O acesso a dados sensíveis foi verificado antes do carregamento?
- [ ] Alguém que não participou do projeto conseguiu usar sem explicação?

## Questões para reflexão

1. "Que decisão essa pessoa vai tomar?" é a pergunta fundadora. O que você faria
   ao descobrir, no meio do projeto, que não existe decisão associada?
2. Um dashboard estratégico e um operacional exigem escolhas opostas de
   granularidade e atualização. O que acontece quando um cliente pede os dois na
   mesma tela?
3. A AED "impede que o dashboard minta". Dê um exemplo concreto de uma mentira
   silenciosa que só a AED revelaria.
4. Limitar-se a 3–5 KPIs é uma restrição autoimposta. Como você negociaria com um
   cliente que quer quinze?
5. Sobre governança: um dashboard de clima organizacional mostra a média de
   satisfação por time. Times pequenos tornam indivíduos identificáveis. Que
   regra você adotaria, e qual o custo analítico dela?

## Teste você mesmo

:::{dropdown} **Q1.** Quais são as três etapas do roteiro, na ordem?
**Resposta:** (1) definir as métricas e o tipo do dashboard; (2) realizar a
análise exploratória de dados; (3) seguir os passos de construção no Streamlit.
Codar é a última etapa, não a primeira.
:::

:::{dropdown} **Q2.** Cite os quatro tipos de dashboard e o horizonte de cada um.
**Resposta:** estratégico (trimestre/ano, "estamos indo bem?"), analítico
(mês/trimestre, "por que aconteceu?"), operacional (agora, "o que está
acontecendo?") e tático (semana/mês, "como estamos executando o plano?").
:::

:::{dropdown} **Q3.** Quais são os quatro critérios de uma boa métrica?
**Resposta:** acionável (quem olha pode influenciá-la), comparável (existe
referência), inequívoca (todos calculam igual) e estável (a definição não muda a
cada reunião).
:::

:::{dropdown} **Q4.** O que a AED entrega ao projeto do dashboard?
**Resposta:** um DataFrame limpo com regras de tratamento documentadas; a lista
curta dos gráficos que realmente comunicam algo, já testados no notebook; e as
faixas realistas para os filtros.
:::

:::{dropdown} **Q5.** Por que desenhar o wireframe antes de codar?
**Resposta:** porque decidir no papel o que fica acima da dobra, o que é filtro e
o que é resultado leva minutos, enquanto reorganizar `st.columns` e reescrever
seções depois leva horas. O desenho também alinha expectativas com o cliente
antes do investimento em código.
:::

:::{dropdown} **Q6.** Sobre governança: esconder uma página do menu protege os dados?
**Resposta:** não. Isso é apresentação, não segurança. A verificação de permissão
precisa ocorrer antes do carregamento do dado sensível, dentro da própria página
— e é preciso considerar também se o download e mesmo os agregados são seguros
(médias de grupos pequenos podem identificar indivíduos).
:::

---

:::{div}
:class: chapter-footer
[← Capítulo 14](../part5/ch14-temas-e-componentes.md) · [Índice](../conteudo.md) ·
[Capítulo 16 → Projeto guiado](./ch16-projeto-guiado.md)
:::
