---
title: "2. Instalação e ambientes virtuais"
subject: "Parte 1: Motivação e Ambiente"
---

# Instalação e ambientes virtuais

:::{admonition} O que você vai aprender
:class: tip
- Por que dashboards pedem máquina local, e não Colab
- O que é um **virtualenv** e por que criar um por projeto
- Como instalar o Streamlit no Windows, macOS e Linux
- Como verificar a instalação com `streamlit hello`
- Como congelar as dependências em `requirements.txt` — o arquivo que o deploy vai exigir
:::

:::{div}
:class: run-quick
**Este capítulo não tem app.** Ele prepara o terreno. O passo a passo executável
está na página de [Setup do ambiente](../setup.md).
:::

## Visão geral

### Por que local?

Um app Streamlit não é um documento — é um **processo servidor**. Ao rodar
`streamlit run app.py`, o Python sobe um servidor web que escuta a porta `8501`
e entrega uma página ao navegador. Ambientes de notebook on-line (Colab,
Kaggle) executam código, mas não expõem portas para a internet de forma direta.
Rodar Streamlit ali exige túneis (`ngrok`, `localtunnel`) que adicionam contas,
tokens, limites de uso e uma camada extra de coisas para quebrar em sala de
aula.

:::{admonition} Recomendação da aula
:class: important
Para a maioria dos frameworks de dashboard em Python — Streamlit, Dash, Panel —
**use a máquina local**. O Colab continua ótimo para a etapa anterior: explorar
os dados e estruturar os gráficos (veja o
[Capítulo 6](../part3/ch06-plotly-express.md)).
:::

### O problema que o virtualenv resolve

Imagine três projetos na mesma máquina:

| Projeto | Precisa de |
| --- | --- |
| Dashboard Finanças | `plotly==5.9`, `pandas==1.5` |
| Dashboard Vendas | `plotly==5.20`, `pandas==2.2` |
| Dashboard Radar 360 | `streamlit==1.28`, uma lib legada |

Se todos instalarem seus pacotes no Python global, o último `pip install` vence
e os outros dois quebram. Pior: você só descobre no dia da apresentação.

Um **ambiente virtual** (virtualenv) é uma pasta isolada com sua própria cópia
do interpretador e sua própria pasta `site-packages`. Instalar `plotly` dentro
dele não afeta nada fora dele.

:::{admonition} Regra prática
:class: tip
**Um virtualenv por projeto.** Sem exceção. O custo é um comando; o benefício é
nunca mais depurar conflito de versão.
:::

```text
projetos/
├── dashboard-financas/
│   ├── st-venv/          ← plotly 5.9,  pandas 1.5
│   └── app.py
├── dashboard-vendas/
│   ├── st-venv/          ← plotly 5.20, pandas 2.2
│   └── app.py
└── dashboard-radar360/
    ├── st-venv/          ← streamlit 1.28
    └── app.py
```

### Anaconda, venv ou conda?

| Opção | Quando escolher |
| --- | --- |
| **`venv`** (padrão do Python) | Sempre que possível. Leve, embutido, é o que o deploy espera. |
| **Anaconda / `conda`** | Windows sem Python instalado, ou dependências científicas pesadas (GDAL, GPU). Já traz pandas, numpy e matplotlib. |
| **`uv` / `poetry`** | Projetos maiores, com controle de lockfile. Fora do escopo desta aula. |

Este livro usa `venv`, com instruções equivalentes para `conda`.

## Mãos à obra

**Passo 1 — Criar e ativar o ambiente.**

::::{tab-set}

:::{tab-item} Windows (PowerShell)
:sync: win

```powershell
cd C:\Projetos\dashboard-vendas
python -m venv st-venv
.\st-venv\Scripts\Activate.ps1
```

Se aparecer *"execution of scripts is disabled"*, libere uma vez:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```
:::

:::{tab-item} macOS / Linux
:sync: mac

```bash
cd ~/projetos/dashboard-vendas
python3 -m venv st-venv
source st-venv/bin/activate
```
:::

:::{tab-item} conda
:sync: conda

```bash
conda create -n dashboard-vendas python=3.12 -y
conda activate dashboard-vendas
```
:::

::::

O prompt passa a mostrar `(st-venv)`. **Se esse prefixo não aparecer, o ambiente
não está ativo** — e tudo o que você instalar vai para o Python global.

**Passo 2 — Instalar os pacotes.**

```bash
pip install --upgrade pip
pip install streamlit pandas numpy plotly matplotlib seaborn pillow
```

| Pacote | Papel no dashboard |
| --- | --- |
| `streamlit` | O framework: widgets, layout, servidor |
| `pandas`, `numpy` | Carga e transformação dos dados |
| `plotly` | Gráficos interativos — o padrão deste livro |
| `matplotlib`, `seaborn` | Gráficos estáticos, via `st.pyplot` |
| `pillow` | Abrir arquivos de imagem para `st.image` |

**Passo 3 — Verificar.**

```bash
streamlit hello
```

O comando abre o app de demonstração oficial no navegador. É o teste de fumaça:
se essa página carregar, a instalação está correta. Encerre com `Ctrl + C`.

```bash
streamlit version
```

**Passo 4 — Congelar as dependências.** O arquivo `requirements.txt` é o
contrato entre a sua máquina e o servidor de deploy. Sem ele, o
[Capítulo 17](../part7/ch17-deploy.md) não funciona.

```bash
pip freeze > requirements.txt
```

:::{admonition} `pip freeze` grava demais
:class: warning
`pip freeze` lista **todos** os pacotes do ambiente, incluindo dependências
transitivas com versões exatas. Isso é reprodutível, mas frágil no deploy (um
pacote indisponível derruba a instalação inteira).

Para um projeto de aula, prefira um `requirements.txt` escrito à mão, só com o
que você realmente importa, usando `>=`:

```text
streamlit>=1.40
pandas>=2.0
plotly>=5.20
```
:::

**Passo 5 — Estrutura mínima do projeto.**

```text
dashboard-vendas/
├── st-venv/            ← ambiente virtual (NÃO versionar)
├── data/
│   └── vendas.csv
├── app.py              ← o dashboard
├── requirements.txt    ← dependências
├── .gitignore          ← ignora st-venv/ e dados grandes
└── README.md
```

Um `.gitignore` mínimo:

```text
st-venv/
__pycache__/
.streamlit/secrets.toml
```

:::{card} **Vá além**
A página de [Setup](../setup.md) traz a tabela completa de erros comuns de
instalação e como resolvê-los.
:::

## Questões para reflexão

1. Um colega diz que não usa virtualenv "porque só tem um projeto". Que cenário
   concreto, daqui a três meses, provaria que ele está errado?
2. `pip freeze` produz reprodutibilidade máxima e fragilidade máxima ao mesmo
   tempo. Como você decidiria entre versões exatas (`==`) e mínimas (`>=`) em um
   projeto que vai ao ar?
3. A pasta `st-venv/` nunca é versionada no Git, mas o `requirements.txt` sempre
   é. Explique essa assimetria em termos do que é *fonte* e do que é *derivado*.
4. Se o Streamlit precisa de uma porta aberta, que implicações isso tem para
   rodá-lo dentro da rede de uma empresa? Quem você precisaria consultar?
5. O Anaconda resolve o problema de instalação no Windows, mas adiciona ~3 GB e
   um segundo gerenciador de pacotes. Em que perfil de turma esse trade-off
   compensa?

## Teste você mesmo

:::{dropdown} **Q1.** O que exatamente um ambiente virtual isola?
**Resposta:** o interpretador Python e a pasta de pacotes instalados
(`site-packages`) daquele projeto. Pacotes instalados dentro do venv não afetam
o Python global nem outros venvs — o que permite versões diferentes da mesma
biblioteca convivendo na mesma máquina.
:::

:::{dropdown} **Q2.** Como você sabe, olhando o terminal, se o ambiente está ativo?
**Resposta:** o prompt exibe o nome do ambiente entre parênteses, por exemplo
`(st-venv) C:\Projetos\...`. Se o prefixo não aparecer, o ambiente não está
ativo e o `pip install` vai para o Python global.
:::

:::{dropdown} **Q3.** Qual comando verifica que o Streamlit foi instalado corretamente?
**Resposta:** `streamlit hello`, que abre o app de demonstração oficial em
`http://localhost:8501`. `streamlit version` confirma a versão instalada.
:::

:::{dropdown} **Q4.** Por que `st-venv/` deve entrar no `.gitignore`?
**Resposta:** porque é conteúdo **derivado**, específico do sistema operacional e
do caminho da máquina, com centenas de megabytes. Ele é reconstruível a partir do
`requirements.txt`, que é a fonte de verdade e esse sim vai para o repositório.
:::

:::{dropdown} **Q5.** Um app funciona na sua máquina e falha no deploy com `ModuleNotFoundError`. Qual é a causa mais provável?
**Resposta:** a dependência está instalada no seu ambiente local mas não consta
do `requirements.txt`, então o servidor de deploy não a instalou. A correção é
adicionar o pacote ao arquivo e publicar de novo.
:::

---

:::{div}
:class: chapter-footer
[← Capítulo 1](./ch01-por-que-streamlit.md) · [Índice](../conteudo.md) ·
[Capítulo 3 → O primeiro app e o modelo de execução](./ch03-primeiro-app-modelo-de-execucao.md)
:::
