---
title: "Dashboards com Streamlit"
subject: "Início"
---

# Dashboards com Streamlit

> *"Uma maneira mais rápida de criar e compartilhar aplicativos de dados."*
> — lema do Streamlit

Este livro-tutorial acompanha a **Aula 05 — Streamlit** da disciplina de
**Análise e Visualização de Dados** (CESAR School). Ele transforma o roteiro da
aula em um material de consulta permanente: 18 capítulos, cada um com
explicação conceitual, código copiável, um aplicativo executável, questões para
reflexão e um quiz de autoavaliação.

:::{admonition} O que este livro é (e o que não é)
:class: tip

**É** um percurso guiado pelas **principais funções da API do Streamlit**, na
ordem em que elas aparecem quando você constrói um dashboard de verdade:
instalar o ambiente → preparar os gráficos → escrever na tela → desenhar →
interagir → organizar o layout → publicar.

**Não é** um substituto da
[documentação oficial](https://docs.streamlit.io/develop/api-reference). Ao
contrário: cada capítulo aponta para a página correspondente da API reference,
para que você desenvolva o hábito de consultá-la.
:::

## Por que um dashboard?

Uma análise exploratória entregue como notebook responde às perguntas de *quem
escreveu o notebook*. Um dashboard responde às perguntas de **quem usa**. A
diferença está na interatividade: o usuário filtra, recorta, compara e chega às
próprias conclusões.

O Streamlit existe para encurtar essa distância. Ele permite que uma pessoa que
sabe Python — e não necessariamente HTML, CSS ou JavaScript — publique uma
interface web funcional a partir de um único arquivo `.py`. Um dashboard mínimo
cabe em três linhas:

```python
import streamlit as st

st.title("Meu primeiro dashboard")
st.write("Olá, turma de AVD!")
```

```bash
streamlit run app.py
```

## Como o livro está organizado

O livro segue exatamente o roteiro de seis etapas apresentado em aula, expandido
em sete partes:

| Parte | Tema | Capítulos |
| --- | --- | --- |
| 1 | Motivação e Ambiente | 1–3 |
| 2 | Elementos de Texto | 4–5 |
| 3 | Dados e Gráficos | 6–8 |
| 4 | Interatividade | 9–11 |
| 5 | Layout e Estrutura | 12–14 |
| 6 | Construindo o Dashboard | 15–16 |
| 7 | Publicação e Recursos | 17–18 |

Cada capítulo é independente o suficiente para ser consultado isoladamente, mas
a leitura em ordem constrói um dashboard completo ao final da Parte 6.

## Pré-requisitos

Você precisa de:

- **Python 3.9 ou superior** instalado localmente (veja o [Setup](./setup.md));
- familiaridade básica com **pandas** (`DataFrame`, `groupby`, filtros);
- noções de **visualização de dados** — se você já fez uma AED com
  Matplotlib/Seaborn/Plotly, está pronto.

Você **não** precisa saber HTML, CSS, JavaScript ou desenvolvimento web.

## Como começar

1. Leia [Como usar este site](./como-usar.md) — 2 minutos.
2. Siga o [Setup](./setup.md) para preparar o ambiente — 10 minutos.
3. Comece pelo [Capítulo 1](./part1/ch01-por-que-streamlit.md).

:::{card} **Roteiro completo**
Todos os capítulos, laboratórios e templates estão listados no
[índice de conteúdo](./conteudo.md).
:::

---

:::{div}
:class: chapter-footer
Material da disciplina de Análise e Visualização de Dados · Eronides F. da Silva
Neto (efsn@cesar.school) · Conteúdo CC-BY-4.0, código MIT.
:::
