---
title: "18. Templates, repositórios e galeria"
subject: "Parte 7: Publicação e Recursos"
---

# Templates, repositórios e galeria

:::{admonition} O que você vai aprender
:class: tip
- Os dois templates deste repositório: `basic.py` e `advanced.py`
- Como usar um template como ponto de partida do seu projeto
- Repositórios open source que valem a leitura, e o que aprender em cada um
- Onde encontrar componentes e apps prontos
- Como usar IA generativa para acelerar — sem terceirizar o entendimento
- Referências bibliográficas e próximos passos
:::

:::{div}
:class: run-quick
**Rode os templates:** `streamlit run templates/basic.py` ·
`streamlit run templates/advanced.py`
:::

## Visão geral

### Os dois templates

Este repositório traz dois pontos de partida, na pasta `templates/`.

**`basic.py`** — dashboard de uma página, ~90 linhas.

```text
config → carga cacheada → filtros na sidebar → KPIs → 2 gráficos → tabela
```

Use quando: a análise é focada, há um único público, e o objetivo é entregar
rápido. É o template certo para a maioria dos trabalhos de disciplina.

**`advanced.py`** — dashboard estruturado, com navegação e módulos.

```text
app (st.navigation) → dados.py (cache) → graficos.py → views/*.py
```

Use quando: há mais de um público, o volume de dados é maior, ou o projeto vai
crescer. Traz cache com TTL, filtros persistentes entre páginas, tratamento de
estado vazio, download e página de metodologia.

**Como usar um template**

```bash
cp templates/basic.py meu_projeto/app.py
cd meu_projeto
python -m venv st-venv && source st-venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Depois, troque, na ordem: (1) a função de carga, para o seu dado; (2) os filtros,
para as suas colunas; (3) os KPIs, para as suas métricas; (4) os gráficos.

### Repositórios open source que valem a leitura

Ler o código de dashboards reais ensina mais rápido que qualquer tutorial. Os
quatro abaixo foram destacados na aula.

| Projeto | O que aprender |
| --- | --- |
| [**Covid-19 data explorer**](https://github.com/cwerner/covid19) | Ingestão de dados públicos, cache com TTL, séries temporais comparadas entre países |
| [**Handover PoC** (SWAST)](https://github.com/Data-Science-at-SWAST/handover_poc) | Dashboard operacional real, em serviço de saúde; tratamento de dados sensíveis |
| [**streamlit-template** (giswqs)](https://github.com/giswqs/streamlit-template) | Apps multipágina com mapas (Folium/Leafmap); boa estrutura de projeto |
| [**Background Removal**](https://github.com/tyler-simons/BackgroundRemoval) | App de processamento de imagem: upload, modelo, download do resultado |

Ao ler um repositório, procure sempre por três coisas: **onde está o cache**,
**como o estado é gerenciado** e **como o layout foi montado**. São as três
decisões que definem a qualidade de um app Streamlit.

### Onde encontrar mais

| Recurso | Endereço | Para quê |
| --- | --- | --- |
| **Documentação** | [docs.streamlit.io](https://docs.streamlit.io) | A fonte de verdade |
| **API reference** | [docs.streamlit.io/develop/api-reference](https://docs.streamlit.io/develop/api-reference) | Assinatura de cada função |
| **App Gallery** | [streamlit.io/gallery](https://streamlit.io/gallery) | Apps completos, com código |
| **Components Hub** | [components.streamlit.app](https://components.streamlit.app/) | Componentes de terceiros |
| **Blog** | [blog.streamlit.io](https://blog.streamlit.io) | Tutoriais e novidades |
| **Fórum** | [discuss.streamlit.io](https://discuss.streamlit.io) | Dúvidas e soluções |
| **Cheat sheet** | [cheat-sheet.streamlit.app](https://cheat-sheet.streamlit.app/) | Referência de uma página |

### Customização com IA generativa

Modelos de linguagem são bons em Streamlit — a API é estável, bem documentada e
muito representada nos dados de treino. Eles aceleram tarefas específicas:

**Onde a IA ajuda de verdade**

- Converter um gráfico do Matplotlib para Plotly;
- Escrever o boilerplate de filtros a partir do `df.dtypes`;
- Explicar uma mensagem de erro obscura;
- Sugerir o layout de colunas para um conjunto de elementos;
- Gerar o `column_config` de uma tabela com muitas colunas;
- Refatorar um `app.py` inchado em módulos.

**Um prompt que funciona** dá contexto, restrições e formato:

```text
Tenho um DataFrame pandas com as colunas:
data (datetime), regiao (str), categoria (str), canal (str),
unidades (int), receita (float), custo (float), satisfacao (float).

Escreva o bloco de filtros de um dashboard Streamlit que:
- fica na sidebar;
- tem multiselect para regiao, categoria e canal (todos selecionados por padrão);
- tem date_input de período com min/max derivados dos dados;
- retorna o DataFrame filtrado via uma função `aplicar_filtros(df, ...)`;
- trata o caso de resultado vazio com st.warning + st.stop.

Use apenas streamlit e pandas. Comente o código em português.
```

:::{admonition} Onde a IA atrapalha
:class: warning
1. **APIs desatualizadas.** Modelos sugerem `st.beta_columns`,
   `st.cache` (depreciada) ou `use_column_width` com frequência. **Sempre confira
   contra a [API reference](https://docs.streamlit.io/develop/api-reference).**
2. **Decisões de projeto.** Que métrica importa, que decisão o dashboard apoia,
   quem pode ver o quê — nada disso está no código, e o modelo não tem como saber.
   Essa é a parte que é sua ([Capítulo 15](../part6/ch15-roteiro-de-dashboard.md)).
3. **Código que roda e mente.** Um agregado plausível sobre uma coluna com `NaN`
   passa despercebido. Valide os números contra o notebook da AED.

A regra: **use IA para escrever o código que você já sabe descrever.** Se você
não consegue descrever o que quer, o problema não é de código.
:::

### Referências bibliográficas

- **Getting Started with Streamlit for Data Science** — Tyler Richards.
  [Repositório](https://github.com/PacktPublishing/Getting-started-with-Streamlit-for-Data-Science)
- **Interactive Dashboards and Data Apps with Plotly and Dash** — Elias Dabbas.
  [Repositório](https://github.com/PacktPublishing/Interactive-Dashboards-and-Data-Apps-with-Plotly-and-Dash)
- **Crafting a dashboard app in Python using Streamlit** — blog oficial.
  [Artigo](https://blog.streamlit.io/crafting-a-dashboard-app-in-python-using-streamlit/)
- **Storytelling with Data** — Cole Nussbaumer Knaflic. (Sobre comunicação, não
  sobre Streamlit — e por isso mesmo essencial.)

### Próximos passos

1. **Refaça o Capítulo 16 com o seu próprio dataset.** É o exercício que
   consolida tudo.
2. **Publique.** Um dashboard que ninguém acessa não foi terminado
   ([Capítulo 17](./ch17-deploy.md)).
3. **Leia um repositório da lista acima**, inteiro, procurando as três decisões
   (cache, estado, layout).
4. **Contribua.** O ecossistema de componentes é aberto — um componente pequeno e
   bem feito é um ótimo projeto de portfólio.

## Questões para reflexão

1. O `basic.py` cabe em uma tela; o `advanced.py` exige navegar entre arquivos.
   Que sinal, no seu projeto, indicaria o momento de migrar de um para o outro?
2. Ler o código de outros dashboards ensina padrões e também vícios. Como você
   distinguiria os dois sem experiência prévia?
3. A IA acelera o código e não decide o projeto. Que parte do trabalho de um
   analista de dados isso valoriza, e que parte desvaloriza?
4. Modelos sugerem APIs depreciadas com frequência. Que hábito de verificação
   você incorporaria ao seu fluxo para que isso não vire dívida técnica?
5. O capítulo sugere publicar como parte de "terminar". Você concorda? Existe
   dashboard legitimamente não publicado?

## Teste você mesmo

:::{dropdown} **Q1.** Quando escolher `basic.py` em vez de `advanced.py`?
**Resposta:** quando a análise é focada, há um único público e o objetivo é
entregar rápido — um dashboard de uma página. O `advanced.py` serve a projetos com
múltiplos públicos, mais dados ou expectativa de crescimento, e traz navegação
multipágina, módulos separados e cache com TTL.
:::

:::{dropdown} **Q2.** Ao ler o código de um dashboard alheio, quais três decisões procurar?
**Resposta:** onde está o cache (o que é recalculado a cada rerun), como o estado
é gerenciado (`session_state`, `query_params`) e como o layout foi montado
(colunas, abas, páginas). São as três decisões que definem a qualidade de um app
Streamlit.
:::

:::{dropdown} **Q3.** Qual o risco mais comum ao pedir código Streamlit a um modelo de linguagem?
**Resposta:** receber APIs depreciadas ou inexistentes — `st.beta_columns`,
`st.cache`, argumentos que mudaram de nome. A verificação contra a API reference
oficial precisa ser parte do fluxo.
:::

:::{dropdown} **Q4.** Onde encontrar a assinatura exata e os argumentos de uma função do Streamlit?
**Resposta:** na API reference oficial,
`docs.streamlit.io/develop/api-reference`, que também indica em qual versão cada
função e argumento foi introduzido.
:::

:::{dropdown} **Q5.** Que parte do trabalho de construir um dashboard a IA generativa **não** resolve?
**Resposta:** as decisões de projeto — qual decisão o dashboard apoia, quais
métricas importam, qual o público, quem pode ver o quê, e se os números estão
corretos em relação à AED. Essas dependem do contexto do negócio, que não está no
código.
:::

---

:::{div}
:class: chapter-footer
[← Capítulo 17](./ch17-deploy.md) · [⌂ Início](../intro.md) ·
[Índice](../conteudo.md)
:::
:::{div}
:class: chapter-footer
**Fim do livro.** Material da disciplina de Análise e Visualização de Dados ·
Eronides F. da Silva Neto (efsn@cesar.school) · CESAR School.
:::
