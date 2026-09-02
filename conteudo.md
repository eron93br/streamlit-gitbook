---
title: "Índice de conteúdo"
subject: "Início"
---

# Índice de conteúdo

18 capítulos em 7 partes, seguindo o roteiro da Aula 05.

## Início

| Página | Conteúdo |
| --- | --- |
| [Apresentação](./intro.md) | O que é este livro e para quem |
| [Como usar este site](./como-usar.md) | Anatomia de um capítulo, laboratórios, convenções |
| [Setup do ambiente](./setup.md) | Python, virtualenv, instalação, dataset |

## Parte 1 · Motivação e Ambiente

| Cap. | Título | Funções principais | Lab |
| --- | --- | --- | --- |
| 1 | [Por que Streamlit?](./part1/ch01-por-que-streamlit.md) | — | [`ch01_lab.py`](./part1/labs/ch01_lab.py) |
| 2 | [Instalação e ambientes virtuais](./part1/ch02-instalacao-e-ambientes.md) | `pip`, `venv` | — |
| 3 | [O primeiro app e o modelo de execução](./part1/ch03-primeiro-app-modelo-de-execucao.md) | `streamlit run`, `st.set_page_config` | [`ch03_lab.py`](./part1/labs/ch03_lab.py) |

## Parte 2 · Elementos de Texto

| Cap. | Título | Funções principais | Lab |
| --- | --- | --- | --- |
| 4 | [`st.write` e os magic commands](./part2/ch04-write-e-magic.md) | `st.write`, magic, `st.write_stream` | [`ch04_lab.py`](./part2/labs/ch04_lab.py) |
| 5 | [Títulos, markdown e mensagens de status](./part2/ch05-titulos-markdown-e-status.md) | `st.title`, `st.header`, `st.markdown`, `st.code`, `st.success` | [`ch05_lab.py`](./part2/labs/ch05_lab.py) |

## Parte 3 · Dados e Gráficos

| Cap. | Título | Funções principais | Lab |
| --- | --- | --- | --- |
| 6 | [Plotly Express: estruture antes de plugar](./part3/ch06-plotly-express.md) | `px.bar`, `px.line`, `px.scatter` | [`ch06_lab.py`](./part3/labs/ch06_lab.py) |
| 7 | [Exibindo dados: dataframe, table e metric](./part3/ch07-exibindo-dados.md) | `st.dataframe`, `st.metric`, `st.column_config` | [`ch07_lab.py`](./part3/labs/ch07_lab.py) |
| 8 | [Funções gráficas e mídia](./part3/ch08-funcoes-graficas-e-midia.md) | `st.plotly_chart`, `st.pyplot`, `st.image` | [`ch08_lab.py`](./part3/labs/ch08_lab.py) |

## Parte 4 · Interatividade

| Cap. | Título | Funções principais | Lab |
| --- | --- | --- | --- |
| 9 | [Widgets de input](./part4/ch09-widgets-de-input.md) | `st.selectbox`, `st.slider`, `st.multiselect`, `st.form` | [`ch09_lab.py`](./part4/labs/ch09_lab.py) |
| 10 | [Session state e o ciclo de rerun](./part4/ch10-session-state-e-rerun.md) | `st.session_state`, `st.rerun`, `st.fragment` | [`ch10_lab.py`](./part4/labs/ch10_lab.py) |
| 11 | [Cache e performance](./part4/ch11-cache-e-performance.md) | `st.cache_data`, `st.cache_resource`, `st.spinner` | [`ch11_lab.py`](./part4/labs/ch11_lab.py) |

## Parte 5 · Layout e Estrutura

| Cap. | Título | Funções principais | Lab |
| --- | --- | --- | --- |
| 12 | [Layouts e containers](./part5/ch12-layouts-e-containers.md) | `st.columns`, `st.tabs`, `st.sidebar`, `st.expander` | [`ch12_lab.py`](./part5/labs/ch12_lab.py) |
| 13 | [Apps multipágina e navegação](./part5/ch13-multipage-e-navegacao.md) | `st.navigation`, `st.Page`, `st.switch_page` | [`ch13_lab.py`](./part5/labs/ch13_lab.py) |
| 14 | [Temas e Components API](./part5/ch14-temas-e-componentes.md) | `config.toml`, `st.components.v1.html` | [`ch14_lab.py`](./part5/labs/ch14_lab.py) |

## Parte 6 · Construindo o Dashboard

| Cap. | Título | Conteúdo | Lab |
| --- | --- | --- | --- |
| 15 | [Roteiro de construção de um dashboard](./part6/ch15-roteiro-de-dashboard.md) | Métricas, AED, wireframe, governança | — |
| 16 | [Projeto guiado: dashboard de vendas](./part6/ch16-projeto-guiado.md) | Do CSV ao app completo em 6 etapas | [`ch16_lab.py`](./part6/labs/ch16_lab.py) |

## Parte 7 · Publicação e Recursos

| Cap. | Título | Conteúdo |
| --- | --- | --- |
| 17 | [Deploy](./part7/ch17-deploy.md) | Streamlit Community Cloud, `requirements.txt`, segredos |
| 18 | [Templates, repositórios e galeria](./part7/ch18-templates-e-galeria.md) | `basic.py`, `advanced.py`, projetos open source |

## Arquivos do repositório

| Caminho | O que é |
| --- | --- |
| `scripts/gerar_dados.py` | Gera o dataset sintético `data/vendas.csv` |
| `templates/basic.py` | Template mínimo de dashboard (uma página) |
| `templates/advanced.py` | Template completo (multipágina, cache, filtros) |
| `requirements.txt` | Dependências dos apps |
| `myst.yml` | Configuração do livro |
| `.github/workflows/deploy.yml` | Publicação automática no GitHub Pages |

---

:::{div}
:class: chapter-footer
[⌂ Início](./intro.md) · [Como usar este site](./como-usar.md) ·
[Setup do ambiente](./setup.md)
:::
