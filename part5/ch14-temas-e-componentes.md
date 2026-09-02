---
title: "14. Temas e Components API"
subject: "Parte 5: Layout e Estrutura"
---

# Temas e Components API

:::{admonition} O que você vai aprender
:class: tip
- Como personalizar cores e fontes com `.streamlit/config.toml`
- As outras opções de configuração que importam (porta, upload, magic)
- O que é a **Components API** e por que ela existe
- Como usar componentes da comunidade (`streamlit-aggrid`, `streamlit-option-menu`, `folium`)
- Como injetar HTML/CSS com `st.html` e `st.components.v1.html` — e os limites disso
- Onde encontrar componentes: Components Hub e App Gallery
:::

:::{div}
:class: run-quick
**Rode este código:** [`part5/labs/ch14_lab.py`](./labs/ch14_lab.py) — tema
customizado, HTML injetado e um cartão de KPI feito à mão.
`streamlit run part5/labs/ch14_lab.py`
:::

:::{div}
:class: api-ref
🔗 **Referência:** [Custom components](https://docs.streamlit.io/develop/api-reference/custom-components)
· [Theming](https://docs.streamlit.io/develop/concepts/configuration/theming)
· [Components Hub](https://components.streamlit.app/)
:::

## Visão geral

### O tema: `.streamlit/config.toml`

O Streamlit lê configurações de um arquivo `config.toml` dentro de uma pasta
`.streamlit/` na raiz do projeto.

```toml
# .streamlit/config.toml

[theme]
base = "light"                    # "light" ou "dark"
primaryColor = "#FF4B4B"          # cor de destaque: botões, sliders, links
backgroundColor = "#FFFFFF"       # fundo da área principal
secondaryBackgroundColor = "#F0F2F6"  # fundo da sidebar e dos cartões
textColor = "#262730"
font = "sans serif"               # "sans serif", "serif" ou "monospace"

[server]
port = 8501
maxUploadSize = 200               # MB por arquivo em st.file_uploader
headless = true                   # não abre o navegador automaticamente

[browser]
gatherUsageStats = false

[runner]
magicEnabled = true               # veja o Capítulo 4
```

| Chave | Efeito visual |
| --- | --- |
| `primaryColor` | Botões primários, sliders, checkboxes, links, foco |
| `backgroundColor` | Fundo da área principal |
| `secondaryBackgroundColor` | Sidebar, `st.container(border=True)`, cabeçalho de tabelas |
| `textColor` | Cor do texto |
| `base` | Define o ponto de partida claro ou escuro |

:::{admonition} Onde colocar o arquivo
:class: tip
`.streamlit/config.toml` na **raiz do projeto** vale para aquele app.
`~/.streamlit/config.toml` vale para todos os apps do usuário. O do projeto tem
precedência — e é o que você versiona no Git, garantindo que o app tenha a mesma
aparência para todo mundo.
:::

Versões recentes permitem também definir fontes customizadas e temas separados
para claro e escuro (`[theme.light]` / `[theme.dark]`) — confira a
documentação de theming da sua versão.

### Configuração por linha de comando

Qualquer chave do `config.toml` pode ser passada na execução:

```bash
streamlit run app.py --server.port 8502
streamlit run app.py --theme.primaryColor "#1c6fd6"
streamlit run app.py --server.headless true
```

Útil para rodar dois apps ao mesmo tempo ou testar variações de tema sem editar
arquivo.

### Components API: o que é

Os elementos nativos cobrem muita coisa, mas não tudo. A **Components API**
permite que qualquer pessoa empacote um front-end (React, Vue, HTML puro) como um
pacote Python instalável com `pip`, que se comunica com o Streamlit nas duas
direções: recebe argumentos do Python e devolve valores de volta.

O resultado é um ecossistema de centenas de componentes de terceiros.

| Componente | O que faz |
| --- | --- |
| `streamlit-aggrid` | Tabela avançada: agrupamento, edição, pivot, filtros por coluna |
| `streamlit-option-menu` | Menu lateral estilizado, alternativa ao radio |
| `streamlit-folium` | Mapas Folium/Leaflet interativos com retorno de clique |
| `streamlit-lottie` | Animações Lottie |
| `streamlit-extras` | Coleção de utilitários pequenos (badges, cartões, atalhos) |
| `streamlit-authenticator` | Login com usuário e senha |
| `plotly-events` | Captura de eventos de clique em figuras Plotly |

Uso típico — instala com pip, importa, usa como qualquer função:

```bash
pip install streamlit-option-menu
```

```python
from streamlit_option_menu import option_menu

with st.sidebar:
    escolha = option_menu(
        "Menu",
        ["Visão geral", "Regiões", "Produtos"],
        icons=["speedometer2", "map", "box"],
        default_index=0,
    )
```

:::{warning}
Componentes de terceiros são **código de terceiros**. Antes de adotar um em um
projeto que vai para produção, verifique: última atualização, número de issues
abertas, compatibilidade com a sua versão do Streamlit e licença. Um componente
abandonado quebra no próximo upgrade — e você não terá controle sobre o
conserto.
:::

### HTML e CSS: `st.html` e `st.components.v1.html`

Para necessidades pontuais, dá para injetar HTML diretamente.

```python
# renderiza HTML/CSS no fluxo da página
st.html("""
<div style="padding:1rem;border-radius:10px;background:#fff1f1;
            border-left:4px solid #ff4b4b">
  <strong>Atenção</strong> — três produtos estão abaixo da meta.
</div>
""")

# renderiza em um iframe isolado — necessário se houver JavaScript
import streamlit.components.v1 as components
components.html("<script>console.log('oi')</script><div>...</div>", height=200)
```

| Função | Isolamento | Aceita JavaScript? |
| --- | --- | --- |
| `st.html` | Renderiza no DOM da página | Não (scripts são removidos) |
| `st.components.v1.html` | `<iframe>` isolado | Sim |
| `st.components.v1.iframe` | `<iframe>` de uma URL externa | Sim (do site remoto) |

A diferença importa: o iframe **não herda** o CSS da página nem consegue alterar
elementos fora dele.

:::{admonition} Sobre injetar CSS com `unsafe_allow_html`
:class: warning
Existe o truque de usar `st.markdown("<style>...</style>", unsafe_allow_html=True)`
para sobrescrever o CSS interno do Streamlit, mirando classes como
`.st-emotion-cache-xxxxx`.

**Funciona e quebra.** Essas classes são geradas automaticamente e mudam a cada
versão. Um upgrade do Streamlit desmonta o seu layout silenciosamente.

Use com parcimônia, para ajustes cosméticos que você aceita perder, e prefira
sempre: (1) o tema do `config.toml`, (2) os containers nativos, (3) um componente
mantido pela comunidade. O CSS bruto é o último recurso.
:::

### Onde procurar

| Recurso | Endereço |
| --- | --- |
| **Components Hub** | [components.streamlit.app](https://components.streamlit.app/) — catálogo pesquisável |
| **Lista oficial** | [streamlit.io/components](https://streamlit.io/components) |
| **App Gallery** | [streamlit.io/gallery](https://streamlit.io/gallery) — apps completos, com código |
| **Fórum** | [discuss.streamlit.io](https://discuss.streamlit.io/) |

## Mãos à obra

**Passo 1 — Criar o tema do projeto.**

```bash
mkdir -p .streamlit
```

```toml
# .streamlit/config.toml
[theme]
base = "light"
primaryColor = "#1c6fd6"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F4F6F9"
textColor = "#1F2126"
font = "sans serif"

[browser]
gatherUsageStats = false
```

Reinicie o app. Botões, sliders e links passam para o azul.

**Passo 2 — Um cartão de KPI customizado.** Quando `st.metric` não basta:

```python
def cartao(titulo: str, valor: str, variacao: str, positivo: bool = True):
    cor = "#16a34a" if positivo else "#dc2626"
    seta = "▲" if positivo else "▼"
    st.html(f"""
    <div style="padding:1rem 1.2rem;border:1px solid #e3e5e9;border-radius:12px;
                background:#fff">
      <div style="font-size:.8rem;color:#5d6169;text-transform:uppercase;
                  letter-spacing:.05em">{titulo}</div>
      <div style="font-size:1.9rem;font-weight:700;line-height:1.2;
                  margin:.2rem 0">{valor}</div>
      <div style="font-size:.9rem;color:{cor};font-weight:600">
        {seta} {variacao}
      </div>
    </div>
    """)

c1, c2, c3 = st.columns(3)
with c1: cartao("Receita", "R$ 9,7 mi", "12,4% vs. 2024", True)
with c2: cartao("Lucro", "R$ 3,1 mi", "8,1% vs. 2024", True)
with c3: cartao("Custo", "R$ 6,6 mi", "14,0% vs. 2024", False)
```

**Passo 3 — Um componente da comunidade.**

```bash
pip install streamlit-option-menu
```

```python
from streamlit_option_menu import option_menu

with st.sidebar:
    pagina = option_menu(
        menu_title="Navegação",
        options=["Visão geral", "Regiões", "Produtos", "Dados"],
        icons=["speedometer2", "map", "box-seam", "table"],
        menu_icon="cast",
        default_index=0,
        styles={"nav-link-selected": {"background-color": "#1c6fd6"}},
    )

st.write(f"Página ativa: **{pagina}**")
```

**Passo 4 — Um iframe externo.**

```python
import streamlit.components.v1 as components

components.iframe(
    "https://docs.streamlit.io/develop/api-reference",
    height=520,
    scrolling=True,
)
```

Útil para embutir um relatório existente, um vídeo ou um painel de outra
ferramenta dentro do seu dashboard.

:::{card} **Vá além**
O laboratório [`ch14_lab.py`](./labs/ch14_lab.py) mostra o mesmo KPI feito com
`st.metric`, com `st.html` e com CSS injetado, para você comparar esforço e
resultado.
:::

## Questões para reflexão

1. O tema fica no `config.toml`, que é versionado. Que problema de consistência
   isso resolve em uma equipe de várias pessoas?
2. Injetar CSS mirando classes internas funciona hoje e quebra amanhã. Como você
   documentaria essa dívida técnica para quem mantiver o app depois de você?
3. A Components API abriu um ecossistema de terceiros. Quais critérios você usaria
   para aprovar (ou vetar) um componente em um projeto corporativo?
4. `st.html` renderiza no DOM da página; `components.html` renderiza em um iframe
   isolado. Que consequência prática esse isolamento tem para estilo e para
   segurança?
5. Personalizar a aparência aproxima o dashboard da identidade visual da empresa e
   afasta-o dos padrões que o usuário já conhece. Onde você traçaria a linha?

## Teste você mesmo

:::{dropdown} **Q1.** Onde fica o arquivo de configuração do tema, e qual chave define a cor de destaque?
**Resposta:** em `.streamlit/config.toml` na raiz do projeto, na seção `[theme]`.
A cor de destaque é `primaryColor`, aplicada a botões primários, sliders,
checkboxes e links.
:::

:::{dropdown} **Q2.** Como rodar dois apps Streamlit ao mesmo tempo na mesma máquina?
**Resposta:** atribuindo portas diferentes:
`streamlit run app1.py` e `streamlit run app2.py --server.port 8502`.
:::

:::{dropdown} **Q3.** O que é a Components API?
**Resposta:** o mecanismo que permite empacotar um front-end próprio (React, Vue,
HTML) como um pacote Python instalável, que troca dados com o Streamlit nas duas
direções. É o que sustenta o ecossistema de componentes de terceiros.
:::

:::{dropdown} **Q4.** Qual a diferença entre `st.html` e `st.components.v1.html`?
**Resposta:** `st.html` renderiza o HTML no DOM da própria página, herdando o CSS,
mas sem executar JavaScript. `st.components.v1.html` renderiza dentro de um
`<iframe>` isolado, que executa JavaScript mas não herda o estilo da página nem
alcança elementos fora dele.
:::

:::{dropdown} **Q5.** Por que injetar CSS mirando classes como `.st-emotion-cache-*` é arriscado?
**Resposta:** porque esses nomes de classe são gerados automaticamente e mudam
entre versões do Streamlit. Um upgrade quebra o estilo silenciosamente, sem erro
visível. Prefira o tema do `config.toml`, os containers nativos ou componentes
mantidos.
:::

:::{dropdown} **Q6.** Onde encontrar componentes de terceiros e apps de exemplo?
**Resposta:** no Components Hub (`components.streamlit.app`), na lista oficial em
`streamlit.io/components`, na App Gallery (`streamlit.io/gallery`) e no fórum
`discuss.streamlit.io`.
:::

---

:::{div}
:class: chapter-footer
[← Capítulo 13](./ch13-multipage-e-navegacao.md) · [Índice](../conteudo.md) ·
[Capítulo 15 → Roteiro de construção de um dashboard](../part6/ch15-roteiro-de-dashboard.md)
:::
