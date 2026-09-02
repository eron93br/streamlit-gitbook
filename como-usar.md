---
title: "Como usar este site"
subject: "Início"
---

# Como usar este site

## A anatomia de um capítulo

Todos os capítulos seguem a mesma estrutura, para que você saiba onde procurar
cada coisa.

:::{admonition} 1 · O que você vai aprender
:class: tip
Uma lista curta com os objetivos do capítulo. Leia antes e releia depois — se
algum item ainda parecer nebuloso, o capítulo não terminou.
:::

:::{div}
:class: run-quick
**2 · Rode este código:** [`part1/labs/ch01_lab.py`](./part1/labs/ch01_lab.py) — a faixa vermelha no
topo de cada capítulo aponta para o app executável correspondente.
:::

**3 · Visão geral** — a explicação conceitual. Por que a função existe, quando
usar, quais armadilhas evitar.

**4 · Mãos à obra** — o passo a passo com código. Os blocos de código nesta
seção são **prévias estáticas com botão de cópia**; o app completo está no
laboratório.

**5 · Questões para reflexão** — perguntas abertas, sem resposta no site. São
para discussão em sala e para você testar se entendeu o *porquê*, não só o
*como*.

**6 · Teste você mesmo** — perguntas objetivas com resposta escondida. Clique na
pergunta para revelar.

:::{dropdown} **Exemplo.** Como se revela a resposta de um quiz?
**Resposta:** clicando no título da pergunta, exatamente como você acabou de
fazer. Tente responder mentalmente antes de abrir.
:::

## Os laboratórios

Diferente de tutoriais de análise de dados, **o Streamlit não roda dentro do
navegador nem dentro de um notebook**. Um app Streamlit é um processo servidor:
você precisa executá-lo na sua máquina com

```bash
streamlit run caminho/do/arquivo.py
```

Por isso os laboratórios deste livro são **arquivos `.py`**, não notebooks. Cada
um é um app completo e independente, que você abre no navegador em
`http://localhost:8501`.

:::{important}
A única exceção é o [Capítulo 6 (Plotly Express)](./part3/ch06-plotly-express.md).
Ali o objetivo é justamente **estruturar os gráficos no notebook antes** de
levá-los para o dashboard — como recomendado em aula.
:::

## Convenções tipográficas

| Convenção | Significado |
| --- | --- |
| `st.função()` | Função da API do Streamlit |
| `bash` nos blocos | Comando de terminal |
| 🔗 **Referência da API** | Link direto para a página oficial daquela função |
| ⚠️ Admonição de alerta | Armadilha comum — leia com atenção |

## Versões

O conteúdo foi escrito e testado com:

| Pacote | Versão mínima |
| --- | --- |
| Python | 3.9 |
| streamlit | 1.40 |
| pandas | 2.0 |
| plotly | 5.20 |

O Streamlit evolui rápido e funções novas aparecem a cada release. Se um exemplo
não funcionar, verifique sua versão com `streamlit version` e consulte a
[API reference](https://docs.streamlit.io/develop/api-reference), que sempre
indica a versão em que cada função foi introduzida.

:::{admonition} `use_container_width` e o novo argumento `width`
:class: warning
Os exemplos deste livro usam `use_container_width=True` para fazer um gráfico ou
tabela ocupar a largura do container. É a forma compatível com o maior número de
versões, e a que você encontrará na maioria do código existente.

Versões recentes do Streamlit substituíram esse argumento por **`width`**, e
`use_container_width` está marcado como depreciado:

| Antigo | Novo |
| --- | --- |
| `use_container_width=True` | `width="stretch"` |
| `use_container_width=False` | `width="content"` |

Ambos funcionam hoje, mas o antigo emite um aviso de depreciação no terminal.
Se você está começando um projeto novo com uma versão recente, **prefira
`width="stretch"`**. Confira a
[API reference](https://docs.streamlit.io/develop/api-reference) da sua versão
para saber qual está disponível.
:::

## Sugestão de uso em aula

- **Antes da aula:** leia a Parte 1 e execute o Setup.
- **Durante a aula:** acompanhe as Partes 2 a 5 rodando os laboratórios.
- **Depois da aula:** faça o projeto guiado da Parte 6 com o seu próprio
  dataset.

---

:::{div}
:class: chapter-footer
[⌂ Início](./intro.md) · [Setup do ambiente](./setup.md) ·
[Índice de conteúdo](./conteudo.md)
:::
