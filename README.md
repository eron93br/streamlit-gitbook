# Dashboards com Streamlit — Tutoriais Interativos

Livro-tutorial em 18 capítulos sobre as principais funções do **Streamlit**,
produzido para a disciplina de **Análise e Visualização de Dados** (CESAR
School). Construído com [MyST / Jupyter Book 2](https://mystmd.org), no mesmo
estilo do [Elements of fMRI Tutorials](https://torwager.github.io/elements-of-fmri-tutorials/book/).

Cada capítulo traz: objetivos de aprendizagem, explicação conceitual, código
copiável, um **app Streamlit executável**, questões para reflexão e um quiz de
autoavaliação com respostas ocultas.

---

## Índice rápido

| Parte | Tema | Capítulos |
| --- | --- | --- |
| 1 | Motivação e Ambiente | Por que Streamlit · Instalação e virtualenvs · Modelo de execução |
| 2 | Elementos de Texto | `st.write` e magic · Títulos, markdown e status |
| 3 | Dados e Gráficos | Plotly Express · `st.dataframe`/`st.metric` · Funções gráficas e mídia |
| 4 | Interatividade | Widgets · `session_state` e rerun · Cache e performance |
| 5 | Layout e Estrutura | Containers · Multipágina · Temas e componentes |
| 6 | Construindo o Dashboard | Roteiro de projeto · Projeto guiado completo |
| 7 | Publicação e Recursos | Deploy · Templates e galeria |

---

## Estrutura do repositório

```text
streamlit-gitbook/
├── myst.yml                   # configuração do livro (título, autores, TOC)
├── README.md
├── requirements.txt           # dependências dos APPS (não do livro)
│
├── intro.md                   # apresentação
├── como-usar.md               # anatomia de um capítulo
├── setup.md                   # preparação do ambiente
├── conteudo.md                # índice completo
│
├── part1/  … part7/           # os 18 capítulos, agrupados em 7 partes
│   ├── chNN-*.md              #   o texto do capítulo
│   └── labs/
│       └── chNN_lab.py        #   o app executável do capítulo
│
├── templates/
│   ├── basic.py               # template de dashboard de uma página
│   └── advanced.py            # template multipágina com perfis e cache
│
├── scripts/
│   └── gerar_dados.py         # gera o dataset sintético
├── data/                      # data/vendas.csv (gerado; não versionado)
│
├── style/custom.css           # estilo do livro
├── landing/index.html         # página inicial do site
└── .github/workflows/
    └── deploy.yml             # publicação automática no GitHub Pages
```

---

## Rodando localmente

Há **duas coisas** para rodar, com pré-requisitos diferentes:

| O que | Precisa de | Comando |
| --- | --- | --- |
| **O livro** (site) | Node.js 18+ | `myst start` |
| **Os apps** (laboratórios) | Python 3.9+ | `streamlit run <arquivo>` |

### 1 · O livro (site MyST)

```bash
# instalar o MyST uma vez, globalmente
npm install -g mystmd

# na raiz do repositório
myst start
```

O servidor sobe em `http://localhost:3000` com recarga automática a cada
alteração nos arquivos `.md`.

Para gerar o site estático:

```bash
myst build --html      # saída em _build/html/
```

### 2 · Os apps Streamlit

```bash
# 2.1 · ambiente virtual (um por projeto — sempre)
python3 -m venv st-venv
source st-venv/bin/activate          # Windows: .\st-venv\Scripts\Activate.ps1

# 2.2 · dependências
pip install --upgrade pip
pip install -r requirements.txt

# 2.3 · gerar o dataset sintético (~4.000 linhas)
python scripts/gerar_dados.py

# 2.4 · rodar qualquer laboratório
streamlit run part1/labs/ch01_lab.py
```

O app abre em `http://localhost:8501`.

### Todos os laboratórios

```bash
streamlit run part1/labs/ch01_lab.py    # Por que Streamlit
streamlit run part1/labs/ch03_lab.py    # Modelo de execução (rerun)
streamlit run part2/labs/ch04_lab.py    # st.write e magic
streamlit run part2/labs/ch05_lab.py    # Texto e status
streamlit run part3/labs/ch06_lab.py    # Plotly Express
streamlit run part3/labs/ch07_lab.py    # dataframe, metric, data_editor
streamlit run part3/labs/ch08_lab.py    # Funções gráficas e mídia
streamlit run part4/labs/ch09_lab.py    # Widgets de input
streamlit run part4/labs/ch10_lab.py    # session_state e fragmentos
streamlit run part4/labs/ch11_lab.py    # Cache e performance
streamlit run part5/labs/ch12_lab.py    # Layouts e containers
streamlit run part5/labs/ch13_lab.py    # Multipágina
streamlit run part5/labs/ch14_lab.py    # Temas e componentes
streamlit run part6/labs/ch16_lab.py    # Dashboard completo

streamlit run templates/basic.py        # template simples
streamlit run templates/advanced.py     # template multipágina
```

### Verificação rápida

```bash
python -m py_compile $(git ls-files '*.py')   # sintaxe de todos os apps
streamlit version                              # versão instalada
```

---

## Deploy

### O livro no GitHub Pages

O workflow em `.github/workflows/deploy.yml` já está pronto: ele instala o MyST,
constrói o site, coloca a landing page na raiz e o livro em `/book/`, e publica.

**Passo 1 — Ajuste o `myst.yml`**

```yaml
project:
  github: https://github.com/SEU-USUARIO/streamlit-gitbook
```

**Passo 2 — Suba para o GitHub**

```bash
git init
git add .
git commit -m "Livro: Dashboards com Streamlit"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/streamlit-gitbook.git
git push -u origin main
```

**Passo 3 — Habilite o Pages**

No repositório: **Settings → Pages → Source → GitHub Actions**.

**Passo 4 — Publique**

Cada `push` na branch `main` dispara o workflow. Acompanhe em **Actions**.
O site fica em:

```text
https://SEU-USUARIO.github.io/streamlit-gitbook/          ← landing page
https://SEU-USUARIO.github.io/streamlit-gitbook/book/     ← o livro
```

O workflow define `BASE_URL` automaticamente a partir do nome do repositório —
se você renomear o repositório, nada precisa ser alterado no código.

#### Publicar o livro na raiz, sem landing page

Se preferir que o livro fique direto na raiz do site, edite
`.github/workflows/deploy.yml`:

```yaml
env:
  BASE_URL: /${{ github.event.repository.name }}
```

```yaml
      - name: Montar o site
        run: |
          mkdir -p dist
          cp -r _build/html/. dist/
```

### Os apps no Streamlit Community Cloud

Os laboratórios também podem ser publicados gratuitamente:

1. Garanta que `requirements.txt` está na raiz e que o dataset foi versionado
   (ou que o app o gera na inicialização — veja abaixo).
2. Acesse [share.streamlit.io](https://share.streamlit.io) e entre com o GitHub.
3. **New app** → selecione o repositório, a branch `main` e o arquivo
   (ex.: `part6/labs/ch16_lab.py`).
4. **Deploy**.

> ⚠️ O `.gitignore` deste repositório **ignora `data/*.csv`**, porque o dataset é
> regenerável. Para publicar um app que depende dele, ou remova essa linha e
> versione o CSV, ou gere os dados dentro da função cacheada de carga.

Detalhes completos, incluindo `st.secrets`, Docker e diagnóstico de erros, estão
no [Capítulo 17 — Deploy](part7/ch17-deploy.md).

---

## O dataset

`scripts/gerar_dados.py` gera `data/vendas.csv` com ~4.000 pedidos ao longo de
24 meses (2024–2025). Não é ruído aleatório: embute sazonalidade mensal, efeito
de fim de semana, margens diferentes por categoria, comissão de marketplace e
crescimento leve ao longo do tempo — de modo que os filtros do dashboard
revelem padrões reais.

| Coluna | Tipo | Descrição |
| --- | --- | --- |
| `data` | date | Data do pedido |
| `regiao` | str | Nordeste, Sudeste, Sul, Centro-Oeste, Norte |
| `categoria` | str | 5 categorias de produto |
| `produto` | str | 20 produtos |
| `canal` | str | E-commerce, Loja física, Marketplace |
| `unidades` | int | Quantidade vendida |
| `preco_unitario` | float | Preço unitário (R$) |
| `receita` | float | `unidades × preco_unitario` |
| `custo` | float | Custo direto (R$) |
| `lucro` | float | `receita − custo` |
| `satisfacao` | float | Nota de 1 a 5 (~1,5% de nulos, propositais) |

```bash
python scripts/gerar_dados.py                       # padrão: 4.000 linhas
python scripts/gerar_dados.py --linhas 20000        # mais volume
python scripts/gerar_dados.py --semente 7           # outra amostra
```

---

## Como adaptar ao seu projeto

1. Copie um template: `cp templates/basic.py meu_projeto/app.py`
2. Troque, **nesta ordem**: a função `carregar()` → os filtros → os KPIs → os
   gráficos.
3. Antes de codar os gráficos, estruture-os no notebook
   ([Capítulo 6](part3/ch06-plotly-express.md)) e siga o roteiro de projeto
   ([Capítulo 15](part6/ch15-roteiro-de-dashboard.md)).

---

## Solução de problemas

| Sintoma | Causa provável | Solução |
| --- | --- | --- |
| `command not found: streamlit` | Virtualenv não ativado | Ative o ambiente antes |
| `ModuleNotFoundError` | Pacote em outro ambiente | `pip install -r requirements.txt` com o venv ativo |
| `FileNotFoundError: data/vendas.csv` | Dataset não gerado | `python scripts/gerar_dados.py` |
| `Port 8501 is already in use` | Outro app rodando | `streamlit run app.py --server.port 8502` |
| `myst: command not found` | MyST não instalado | `npm install -g mystmd` |
| Links quebrados no site publicado | `BASE_URL` incorreta | Confira o nome do repositório no workflow |

---

## Licença

- **Conteúdo** (textos, capítulos, figuras): [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/)
- **Código** (apps, templates, scripts): MIT

## Créditos

Material da disciplina de **Análise e Visualização de Dados** — Eronides F. da
Silva Neto (<efsn@cesar.school>), CESAR School.


Referência técnica: [Streamlit API reference](https://docs.streamlit.io/develop/api-reference).
