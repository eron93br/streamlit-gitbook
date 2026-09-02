---
title: "1. Por que Streamlit?"
subject: "Parte 1: Motivação e Ambiente"
---

# Por que Streamlit?

:::{admonition} O que você vai aprender
:class: tip
- Que problema o Streamlit resolve e por que ele encurta a distância entre uma análise e um produto de dados
- Como o Streamlit se posiciona frente a Dash, Gradio, Power BI e notebooks
- O vocabulário essencial: *app*, *script*, *rerun*, *widget*, *componente*
- Quando **não** usar Streamlit
:::

:::{div}
:class: run-quick
**Rode este código:** [`part1/labs/ch01_lab.py`](./labs/ch01_lab.py) — um app de
15 linhas que já é um dashboard. Execute com
`streamlit run part1/labs/ch01_lab.py`.
:::

## Visão geral

Você terminou a análise exploratória. O notebook tem doze células, quatro
gráficos e uma conclusão bem fundamentada. Você manda o `.ipynb` para a área de
negócio e recebe de volta: *"Dá para ver só a região Nordeste?"*

Você edita a célula, roda de novo, exporta um PNG, responde o e-mail. No dia
seguinte: *"E só o canal de e-commerce?"*

Esse ciclo é o problema. A análise é sua, mas as perguntas são de outra pessoa —
e cada pergunta nova custa uma rodada de ida e volta. Um **dashboard** inverte
isso: você entrega o mecanismo de filtragem junto com o gráfico, e quem tem a
pergunta responde a si mesmo.

O obstáculo histórico era o custo dessa entrega. Publicar uma interface web
significava HTML, CSS, JavaScript, um framework de front-end, uma API de
back-end e um servidor. Um analista de dados que domina pandas raramente domina
esse conjunto — e não deveria precisar.

### A proposta do Streamlit

O Streamlit é um framework Python de código aberto cuja tese é simples:
**um script Python já é uma interface**. Você escreve o script de cima para
baixo, como escreveria um notebook, e o Streamlit traduz cada linha em um
elemento na tela.

```python
import streamlit as st
import pandas as pd

df = pd.read_csv("data/vendas.csv")

st.title("Vendas 2024–2025")
regiao = st.selectbox("Região", sorted(df["regiao"].unique()))
st.metric("Receita", f"R$ {df[df.regiao == regiao].receita.sum():,.0f}")
st.bar_chart(df[df.regiao == regiao].groupby("categoria")["receita"].sum())
```

Sete linhas úteis. Um título, um filtro funcional, um indicador e um gráfico —
servidos em `http://localhost:8501`, atualizando sozinhos quando o usuário troca
a região. Não há rota, callback, template nem estado explícito.

:::{admonition} O mantra da aula
:class: important
> Construa dashboards práticos e funcionais com comandos Python a partir das
> suas visualizações interativas (Plotly) e de pacotes como Seaborn/Matplotlib.

O Streamlit não substitui suas bibliotecas de visualização. Ele **hospeda** os
gráficos que você já sabe fazer.
:::

### O modelo mental em uma frase

> **A cada interação, o Streamlit reexecuta o script inteiro, de cima para
> baixo.**

Guarde essa frase. Ela explica quase tudo que parece estranho no Streamlit — por
que variáveis "esquecem" seu valor, por que um cálculo lento trava a interface,
por que precisamos de `st.session_state` e de `st.cache_data`. Voltaremos a ela
no [Capítulo 3](./ch03-primeiro-app-modelo-de-execucao.md).

### Onde o Streamlit se encaixa

| Ferramenta | Ponto forte | Custo |
| --- | --- | --- |
| **Notebook (Jupyter/Colab)** | Exploração, narrativa, reprodutibilidade | Interatividade limitada; usuário precisa saber ler código |
| **Streamlit** | Prototipagem rápida de apps de dados em Python puro | Menos controle fino do layout; um script por app |
| **Dash (Plotly)** | Controle detalhado, callbacks explícitos, apps corporativos grandes | Curva de aprendizado maior; mais código para o mesmo resultado |
| **Gradio** | Demonstrações de modelos de ML (entrada → saída) | Pouco orientado a dashboards analíticos |
| **Power BI / Tableau** | Governança, conectores prontos, adoção corporativa | Licença paga; lógica em Python limitada |

Na prática, a escolha costuma ser entre **Streamlit** (velocidade) e **Dash**
(controle). Para uma disciplina de Análise e Visualização de Dados — e para a
maioria dos protótipos — a velocidade vence.

### Quando **não** usar Streamlit

Ser honesto sobre os limites é parte de dominar a ferramenta.

- **Aplicações com muitos usuários simultâneos e sessões pesadas.** Cada sessão
  reexecuta o script; sem cache adequado, isso escala mal.
- **Interfaces com layout muito específico.** Se o requisito é pixel-perfect,
  você vai brigar com o framework.
- **Fluxos transacionais** (cadastros, autenticação complexa, escrita crítica em
  banco). O Streamlit é ótimo para *ler e visualizar*, não para ser o sistema de
  registro.
- **Quando um gráfico estático resolve.** Um `.png` no e-mail às vezes é a
  resposta certa.

## Mãos à obra

**Passo 1 — O menor dashboard possível.** Crie `app.py` com três linhas e
execute.

```python
import streamlit as st

st.title("Meu primeiro app")
st.write("Se você está lendo isto no navegador, o Streamlit está funcionando.")
```

```bash
streamlit run app.py
```

**Passo 2 — Adicione um dado e um controle.** A diferença entre uma página e um
dashboard é o widget.

```python
import streamlit as st
import pandas as pd

df = pd.DataFrame(
    {"mes": ["Jan", "Fev", "Mar", "Abr"], "receita": [120, 145, 98, 176]}
)

st.title("Receita mensal")

limite = st.slider("Receita mínima (mil R$)", 0, 200, 100)
filtrado = df[df["receita"] >= limite]

st.bar_chart(filtrado.set_index("mes"))
st.write(f"{len(filtrado)} de {len(df)} meses acima do limite.")
```

Arraste o slider. O gráfico e o texto se atualizam juntos, porque o script
inteiro rodou de novo com o novo valor de `limite`. **É esse o mecanismo.**

**Passo 3 — Compare com o notebook.** Abra o mesmo dado em um notebook e tente
oferecer o mesmo controle a um colega. Você vai precisar de `ipywidgets`, de um
kernel ativo e de alguém disposto a rodar células. O app resolve com uma URL.

:::{card} **Vá além**
O laboratório [`ch01_lab.py`](./labs/ch01_lab.py) reúne os três passos em um app
comentado, já lendo o dataset de vendas do livro.
:::

## Questões para reflexão

1. Pense em uma análise que você entregou recentemente como notebook ou slide.
   Quais perguntas de follow-up você recebeu? Quantas delas um único widget
   teria respondido sozinho?
2. O Streamlit reexecuta o script inteiro a cada interação. Liste dois tipos de
   operação que isso torna caro, e imagine — antes de ler o Capítulo 11 — como
   você evitaria repeti-las.
3. A tabela comparativa acima coloca "controle fino do layout" como custo do
   Streamlit. Em que situação profissional esse custo seria inaceitável, e por
   quê?
4. Um dashboard entrega o mecanismo de filtragem ao usuário. Que tipo de erro de
   interpretação isso **cria**, que não existia quando você entregava um gráfico
   pronto?
5. Se o dashboard responde às perguntas de quem usa, quem decide **quais**
   perguntas são possíveis? Que responsabilidade isso coloca sobre quem
   constrói?

## Teste você mesmo

:::{dropdown} **Q1.** Em uma frase, qual é o modelo de execução do Streamlit?
**Resposta:** a cada interação do usuário (ou a cada salvamento do arquivo), o
Streamlit reexecuta o script Python inteiro, de cima para baixo, e redesenha a
página com o resultado.
:::

:::{dropdown} **Q2.** O Streamlit substitui o Plotly, o Matplotlib e o Seaborn?
**Resposta:** não. Ele é a camada de interface que *hospeda* as figuras
produzidas por essas bibliotecas, via funções como `st.plotly_chart` e
`st.pyplot`. As figuras continuam sendo feitas do jeito que você já sabe.
:::

:::{dropdown} **Q3.** Qual comando de terminal inicia um app Streamlit, e em qual endereço ele fica disponível por padrão?
**Resposta:** `streamlit run app.py`. Por padrão o app é servido em
`http://localhost:8501`.
:::

:::{dropdown} **Q4.** Cite duas situações em que o Streamlit é a escolha errada.
**Resposta:** (a) aplicações transacionais com autenticação complexa e escrita
crítica em banco — o Streamlit é orientado a leitura e visualização; (b)
interfaces que exigem layout pixel-perfect ou componentes muito customizados;
(c) sistemas com grande volume de usuários simultâneos e sessões pesadas, onde o
modelo de rerun escala mal sem cache cuidadoso. Duas quaisquer bastam.
:::

:::{dropdown} **Q5.** Qual é a diferença essencial entre entregar um notebook e entregar um dashboard?
**Resposta:** o notebook entrega **respostas** às perguntas de quem o escreveu;
o dashboard entrega o **mecanismo** para que quem usa formule e responda as
próprias perguntas, sem uma nova rodada com o analista.
:::

---

:::{div}
:class: chapter-footer
[⌂ Início](../intro.md) · [Índice](../conteudo.md) ·
[Capítulo 2 → Instalação e ambientes virtuais](./ch02-instalacao-e-ambientes.md)
:::
