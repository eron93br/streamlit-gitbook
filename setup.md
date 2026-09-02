---
title: "Setup do ambiente"
subject: "Início"
---

# Setup do ambiente

Este capítulo prepara sua máquina em cerca de 10 minutos. Se você já tem Python
e um ambiente virtual funcionando, pule direto para o
[passo 3](#passo-3).

:::{admonition} Por que localmente, e não no Colab?
:class: important
Um app Streamlit é um **servidor web**. Ele abre uma porta (`8501` por padrão) e
serve uma página para o navegador. Ambientes de notebook on-line não expõem
portas de forma direta, então tentativas de rodar Streamlit no Colab exigem
gambiarras de túnel (`ngrok`, `localtunnel`) que quebram com frequência.

Para dashboards, **use a máquina local**. É a recomendação da aula e a que este
livro assume.
:::

## Passo 1 · Obter o Python

::::{tab-set}

:::{tab-item} Windows
:sync: win

A forma mais simples é instalar o **Anaconda**, uma distribuição do Python
voltada para ciência de dados que já traz pandas, numpy, matplotlib e o
gerenciador `conda` pré-instalados.

1. Baixe em [anaconda.com/download](https://www.anaconda.com/download).
2. Durante a instalação, marque a opção de adicionar o Anaconda ao `PATH` (ou
   use sempre o **Anaconda Prompt**).
3. Verifique no PowerShell ou Anaconda Prompt:

```powershell
python --version
pip --version
```

Alternativa mais enxuta: instale o Python direto da
[python.org](https://www.python.org/downloads/windows/), marcando
**"Add python.exe to PATH"** na primeira tela do instalador.
:::

:::{tab-item} macOS
:sync: mac

O macOS traz uma versão antiga do Python. Instale uma atual com o
[Homebrew](https://brew.sh):

```bash
brew install python@3.12
python3 --version
```
:::

:::{tab-item} Linux
:sync: linux

A maioria das distribuições já traz Python 3. Garanta o módulo `venv`:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
python3 --version
```
:::

::::

## Passo 2 · Criar um ambiente virtual

Um **virtualenv** é uma pasta isolada com sua própria cópia do Python e seus
próprios pacotes. Ele evita que o dashboard de Vendas, que precisa de
`plotly==5.20`, quebre o dashboard de Finanças, que precisa de `plotly==5.9`.

:::{admonition} Regra prática
:class: tip
**Um virtualenv por projeto/dashboard.** Sempre.
:::

::::{tab-set}

:::{tab-item} Windows (PowerShell)
:sync: win

```powershell
# na pasta do projeto
python -m venv st-venv
.\st-venv\Scripts\Activate.ps1
```

Se o PowerShell bloquear o script de ativação, libere a execução para o usuário
atual (uma única vez):

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```
:::

:::{tab-item} macOS / Linux
:sync: mac

```bash
# na pasta do projeto
python3 -m venv st-venv
source st-venv/bin/activate
```
:::

:::{tab-item} conda
:sync: conda

```bash
conda create -n st-venv python=3.12
conda activate st-venv
```
:::

::::

Com o ambiente ativo, o prompt passa a exibir o prefixo `(st-venv)`. Para sair,
use `deactivate`.

(passo-3)=
## Passo 3 · Instalar as dependências

Com o virtualenv **ativo**:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Ou, se você não clonou o repositório, instale os pacotes diretamente:

```bash
pip install streamlit pandas numpy plotly matplotlib seaborn pillow
```

| Pacote | Para quê |
| --- | --- |
| `streamlit` | O framework do dashboard |
| `pandas` / `numpy` | Manipulação dos dados |
| `plotly` | Gráficos interativos (recomendado) |
| `matplotlib` / `seaborn` | Gráficos estáticos |
| `pillow` | Abrir imagens para o `st.image` |

## Passo 4 · Verificar a instalação

```bash
streamlit hello
```

Esse comando abre no navegador o app de demonstração oficial, em
`http://localhost:8501`. Se a página carregar, **está tudo pronto**. Encerre com
`Ctrl + C` no terminal.

Confira também a versão instalada:

```bash
streamlit version
```

## Passo 5 · Gerar o dataset dos exemplos

Os laboratórios usam um dataset sintético de vendas gerado localmente — nenhum
download é necessário.

```bash
python scripts/gerar_dados.py
```

Isso cria `data/vendas.csv` (~4.000 linhas) com as colunas `data`, `regiao`,
`categoria`, `produto`, `canal`, `unidades`, `preco_unitario`, `receita`,
`custo`, `lucro` e `satisfacao`.

## Rodando um app

```bash
streamlit run part1/labs/ch03_lab.py
```

O navegador abre automaticamente. Toda vez que você salvar o arquivo, o
Streamlit detecta a mudança e oferece o botão **"Rerun"** no canto superior
direito — ative **"Always rerun"** para recarregar sozinho.

:::{admonition} Erros comuns
:class: warning

| Sintoma | Causa provável | Solução |
| --- | --- | --- |
| `command not found: streamlit` | Virtualenv não ativado | Ative o ambiente antes |
| `ModuleNotFoundError: plotly` | Pacote instalado em outro ambiente | Reinstale com o venv ativo |
| `Port 8501 is already in use` | Outro app rodando | `streamlit run app.py --server.port 8502` |
| Página em branco | Erro no script | Veja o traceback no terminal |
| `FileNotFoundError: data/vendas.csv` | Dataset não gerado | Rode `python scripts/gerar_dados.py` |
:::

---

:::{div}
:class: chapter-footer
[⌂ Início](./intro.md) · [Como usar este site](./como-usar.md) ·
[Capítulo 1 →](./part1/ch01-por-que-streamlit.md)
:::
