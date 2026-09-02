---
title: "17. Deploy"
subject: "Parte 7: Publicação e Recursos"
---

# Deploy

:::{admonition} O que você vai aprender
:class: tip
- O que precisa estar no repositório antes de publicar
- Publicar no **Streamlit Community Cloud** — o caminho gratuito e mais curto
- Gerenciar segredos com `st.secrets` e `secrets.toml`
- Erros de deploy mais comuns e como diagnosticá-los
- Outras opções: Docker, Hugging Face Spaces, servidor próprio
- Como publicar **este livro** no GitHub Pages
:::

:::{div}
:class: run-quick
**Este capítulo não tem app.** Ele publica os que você já construiu.
:::

:::{div}
:class: api-ref
🔗 **Referência:** [Deploy your app](https://docs.streamlit.io/deploy)
· [Community Cloud](https://share.streamlit.io/)
· [`st.secrets`](https://docs.streamlit.io/develop/api-reference/connections/st.secrets)
:::

## Visão geral

### O que o repositório precisa ter

Todo serviço de deploy espera a mesma coisa: um repositório Git com o script do
app e a lista de dependências.

```text
dashboard-vendas/
├── app.py                  ← ponto de entrada
├── requirements.txt        ← OBRIGATÓRIO
├── dados.py
├── graficos.py
├── data/vendas.csv         ← se o dado vier junto
├── .streamlit/
│   └── config.toml         ← tema (versionado)
└── .gitignore              ← ignora venv e secrets.toml
```

:::{warning}
**Nunca versione `.streamlit/secrets.toml`.** Ele contém senhas e tokens. Garanta
que o `.gitignore` tem a linha `.streamlit/secrets.toml` **antes** do primeiro
commit — um segredo que já foi para o histórico do Git continua lá mesmo depois
de removido do arquivo.
:::

`requirements.txt` mínimo:

```text
streamlit>=1.40
pandas>=2.0
plotly>=5.20
```

### Streamlit Community Cloud

O caminho gratuito, feito pela própria Streamlit e integrado ao GitHub.

**Pré-requisitos:** conta no GitHub, repositório **público** (o plano gratuito
tem cota de apps privados), `requirements.txt` na raiz.

**Passo a passo:**

1. Suba o projeto para o GitHub:

```bash
git init
git add .
git commit -m "Dashboard de vendas"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/dashboard-vendas.git
git push -u origin main
```

2. Acesse [share.streamlit.io](https://share.streamlit.io) e entre com o GitHub.
3. Clique em **New app** e selecione repositório, branch (`main`) e o caminho do
   arquivo principal (`app.py`).
4. Em **Advanced settings**, escolha a versão do Python e cole os segredos, se
   houver.
5. **Deploy**. O build leva de 2 a 5 minutos.

O app fica em `https://SEU-APP.streamlit.app`. Cada `git push` no branch
publicado dispara um novo deploy automaticamente.

| Recurso | Limite típico do plano gratuito |
| --- | --- |
| Memória por app | ~1 GB |
| Apps públicos | Vários |
| Apps privados | Cota reduzida |
| Hibernação | O app "dorme" após dias sem acesso e acorda no primeiro acesso |

:::{admonition} Consulte os limites atuais
:class: tip
Cotas e limites mudam. Confira a página oficial do
[Community Cloud](https://streamlit.io/cloud) antes de assumir qualquer número
em um projeto que importa.
:::

### Segredos: `st.secrets`

Credenciais nunca vão no código. O Streamlit lê um arquivo TOML e o expõe como um
dicionário.

```toml
# .streamlit/secrets.toml   (LOCAL — nunca commitado)
api_key = "sk-abc123"

[db]
url = "postgresql://usuario:senha@host:5432/base"

[email]
remetente = "dashboard@empresa.com"
```

```python
import streamlit as st

chave = st.secrets["api_key"]
url = st.secrets["db"]["url"]
```

**Em produção**, o mesmo conteúdo é colado no painel do Community Cloud
(*Settings → Secrets*). O código não muda — `st.secrets` lê de onde estiver
disponível.

```python
@st.cache_resource
def conexao():
    from sqlalchemy import create_engine
    return create_engine(st.secrets["db"]["url"], pool_pre_ping=True)
```

### Erros comuns de deploy

| Sintoma | Causa | Correção |
| --- | --- | --- |
| `ModuleNotFoundError` | Pacote ausente no `requirements.txt` | Adicione e faça push |
| `FileNotFoundError` | Caminho relativo à sua máquina | Use `Path(__file__).parent / "data" / "x.csv"` |
| App reinicia sozinho | Estouro de memória | Reduza o dataset, use Parquet, cacheie melhor |
| Build muito lento | `requirements.txt` gerado por `pip freeze` | Liste só o que você importa |
| `KeyError` em `st.secrets` | Segredos não configurados no painel | Cole o TOML em Settings → Secrets |
| Fontes/imagens não carregam | Arquivo não versionado | Verifique se o `.gitignore` não o excluiu |
| Erro de versão do Python | Padrão do serviço difere do local | Fixe em Advanced settings ou em `runtime.txt` |

Os logs ficam no menu **Manage app** (canto inferior direito do app publicado) —
é o primeiro lugar a olhar quando algo falha.

### Outras opções

**Docker** — para servidor próprio ou nuvem corporativa:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1
ENTRYPOINT ["streamlit", "run", "app.py", \
            "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t dashboard-vendas .
docker run -p 8501:8501 dashboard-vendas
```

**Hugging Face Spaces** — crie um Space com SDK "Streamlit", envie o código e
adicione `requirements.txt`. Gratuito, com hardware básico.

**Servidor próprio** — rode o Streamlit atrás de um proxy reverso (nginx) com
HTTPS e autenticação. É o caminho quando os dados não podem sair da rede.

## Publicando este livro no GitHub Pages

O livro que você está lendo é um site estático gerado pelo
[MyST](https://mystmd.org). O repositório já traz o workflow pronto em
`.github/workflows/deploy.yml`.

**Passo 1 — Testar localmente.**

```bash
npm install -g mystmd
myst start          # servidor de desenvolvimento com recarga automática
```

**Passo 2 — Configurar o Pages.** No repositório do GitHub:
**Settings → Pages → Source → GitHub Actions**.

**Passo 3 — Publicar.**

```bash
git add .
git commit -m "Publica o livro"
git push origin main
```

O workflow instala o MyST, roda `myst build --html`, monta a landing page na raiz
e o livro em `/book/`, e publica. Acompanhe em **Actions**.

O site fica em `https://SEU-USUARIO.github.io/NOME-DO-REPO/`.

:::{important}
Ajuste o campo `github:` no `myst.yml` para a URL do **seu** repositório. Ele
alimenta os links de "editar esta página" e os metadados do site.
:::

## Questões para reflexão

1. Um segredo commitado por engano continua no histórico do Git mesmo após ser
   removido. Que procedimento você adotaria ao descobrir isso em um projeto real?
2. O Community Cloud hiberna apps sem acesso. Que impacto isso tem sobre a
   percepção de confiabilidade, e como você comunicaria isso aos usuários?
3. `pip freeze` produz builds lentos e frágeis. Como você equilibraria
   reprodutibilidade e resiliência no `requirements.txt` de um app em produção?
4. Publicar um dashboard em repositório público expõe o código **e** os dados de
   exemplo. Que verificação você faria antes de tornar um repositório público?
5. Docker adiciona uma camada de complexidade. Em que ponto de maturidade de um
   projeto ela passa a compensar?

## Teste você mesmo

:::{dropdown} **Q1.** Quais arquivos são indispensáveis no repositório para publicar um app no Community Cloud?
**Resposta:** o script principal (`app.py` ou equivalente) e o `requirements.txt`
na raiz. O `.streamlit/config.toml` é opcional mas recomendado; o
`.streamlit/secrets.toml` **não** deve ser versionado.
:::

:::{dropdown} **Q2.** Como o app acessa uma senha de banco sem tê-la no código?
**Resposta:** por `st.secrets`, que lê o arquivo `.streamlit/secrets.toml`
localmente e, em produção, o conteúdo colado no painel de Settings → Secrets.
Acesso via `st.secrets["db"]["url"]`.
:::

:::{dropdown} **Q3.** O app funciona local e falha no deploy com `FileNotFoundError`. Causa provável?
**Resposta:** o caminho do arquivo é relativo ao diretório de execução da sua
máquina. A correção é construir o caminho a partir do próprio módulo:
`Path(__file__).parent / "data" / "vendas.csv"`.
:::

:::{dropdown} **Q4.** O que dispara um novo deploy no Community Cloud?
**Resposta:** qualquer `git push` no branch configurado. O serviço observa o
repositório e reconstrói o app automaticamente.
:::

:::{dropdown} **Q5.** Onde ver os logs de um app publicado que está falhando?
**Resposta:** no menu **Manage app**, no canto inferior direito da página do app
publicado. É o primeiro lugar a consultar em qualquer falha de deploy.
:::

:::{dropdown} **Q6.** Que porta e endereço um container Docker do Streamlit precisa expor?
**Resposta:** a porta 8501, com o endereço `0.0.0.0` para aceitar conexões
externas ao container:
`streamlit run app.py --server.port=8501 --server.address=0.0.0.0`.
:::

---

:::{div}
:class: chapter-footer
[← Capítulo 16](../part6/ch16-projeto-guiado.md) · [Índice](../conteudo.md) ·
[Capítulo 18 → Templates e galeria](./ch18-templates-e-galeria.md)
:::
