"""Laboratório 14 — Temas, HTML customizado e Components API.

O mesmo cartão de KPI feito de três formas, para comparar esforço e resultado.

Execute na raiz do repositório:
    streamlit run part5/labs/ch14_lab.py
"""

from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Lab 14 · Temas e componentes", page_icon="🎨",
                   layout="wide")

RAIZ = Path(__file__).resolve().parents[2]
CSV = RAIZ / "data" / "vendas.csv"

if not CSV.exists():
    st.error("Rode `python scripts/gerar_dados.py` na raiz do repositório.")
    st.stop()


@st.cache_data
def carregar() -> pd.DataFrame:
    return pd.read_csv(CSV, parse_dates=["data"])


df = carregar()
receita = df["receita"].sum()
lucro = df["lucro"].sum()
custo = df["custo"].sum()

st.title("🎨 Lab 14 — Temas e Components API")

a1, a2, a3, a4 = st.tabs(
    ["1 · Tema", "2 · KPI de três formas", "3 · HTML e iframe", "4 · Componentes"]
)

# ==========================================================================
with a1:
    st.header("O arquivo `.streamlit/config.toml`")

    esq, dir_ = st.columns(2, gap="large")

    with esq:
        st.code(
            '''# .streamlit/config.toml

[theme]
base = "light"                        # "light" ou "dark"
primaryColor = "#FF4B4B"              # botões, sliders, links
backgroundColor = "#FFFFFF"           # fundo principal
secondaryBackgroundColor = "#F0F2F6"  # sidebar e cartões
textColor = "#262730"
font = "sans serif"

[server]
port = 8501
maxUploadSize = 200                   # MB por arquivo
headless = true

[browser]
gatherUsageStats = false

[runner]
magicEnabled = true''',
            language="toml",
            line_numbers=True,
        )

        st.info(
            "O arquivo na raiz do projeto vale para aquele app e **é "
            "versionado no Git** — garantindo a mesma aparência para toda a "
            "equipe. O `~/.streamlit/config.toml` vale para todos os apps do "
            "usuário e tem precedência menor."
        )

    with dir_:
        st.subheader("Elementos que respondem ao tema")
        st.button("Botão primário", type="primary", use_container_width=True)
        st.button("Botão secundário", use_container_width=True)
        st.slider("Slider", 0, 100, 60)
        st.checkbox("Checkbox", value=True)
        st.toggle("Toggle", value=True)
        st.progress(0.62, text="Barra de progresso")
        with st.container(border=True):
            st.caption("`st.container(border=True)` usa o fundo secundário.")
            st.metric("Receita", f"R$ {receita:,.0f}")

        st.divider()
        st.subheader("Configuração por linha de comando")
        st.code(
            """streamlit run app.py --server.port 8502
streamlit run app.py --theme.primaryColor "#1c6fd6\"""",
            language="bash",
        )

# ==========================================================================
with a2:
    st.header("O mesmo KPI, três implementações")

    c1, c2, c3 = st.columns(3, gap="large")

    # --- 1. Nativo ---
    with c1:
        st.subheader("1 · `st.metric`")
        st.metric("Receita", f"R$ {receita:,.0f}", "+12,4%", border=True)
        st.metric("Custo", f"R$ {custo:,.0f}", "+14,0%",
                  delta_color="inverse", border=True)
        st.success("✅ Uma linha. Acessível, responsivo, segue o tema.")
        st.code(
            'st.metric("Receita", valor, "+12,4%", border=True)',
            language="python",
        )

    # --- 2. st.html ---
    with c2:
        st.subheader("2 · `st.html`")

        def cartao(titulo: str, valor: str, variacao: str, positivo: bool):
            cor = "#16a34a" if positivo else "#dc2626"
            seta = "▲" if positivo else "▼"
            st.html(f"""
            <div style="padding:1rem 1.2rem;border:1px solid #e3e5e9;
                        border-radius:12px;background:#fff;margin-bottom:.6rem">
              <div style="font-size:.78rem;color:#5d6169;text-transform:uppercase;
                          letter-spacing:.06em">{titulo}</div>
              <div style="font-size:1.9rem;font-weight:700;line-height:1.2;
                          margin:.15rem 0;color:#1f2126">{valor}</div>
              <div style="font-size:.9rem;color:{cor};font-weight:600">
                {seta} {variacao}
              </div>
            </div>
            """)

        cartao("Receita", f"R$ {receita:,.0f}", "12,4% vs. ano anterior", True)
        cartao("Custo", f"R$ {custo:,.0f}", "14,0% vs. ano anterior", False)
        st.warning(
            "⚠️ Controle total do visual, mas as cores estão fixas no código — "
            "não seguem o tema claro/escuro do usuário."
        )

    # --- 3. CSS injetado ---
    with c3:
        st.subheader("3 · CSS injetado")
        st.markdown(
            """
            <style>
            .kpi-custom {
                background: linear-gradient(135deg, #ff4b4b 0%, #c53030 100%);
                color: #fff; padding: 1.2rem; border-radius: 12px;
                margin-bottom: .6rem;
            }
            .kpi-custom .rot { font-size:.78rem; opacity:.85;
                               text-transform:uppercase; letter-spacing:.06em }
            .kpi-custom .val { font-size:1.9rem; font-weight:700; line-height:1.2 }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""<div class="kpi-custom">
                  <div class="rot">Receita</div>
                  <div class="val">R$ {receita:,.0f}</div>
                </div>
                <div class="kpi-custom">
                  <div class="rot">Lucro</div>
                  <div class="val">R$ {lucro:,.0f}</div>
                </div>""",
            unsafe_allow_html=True,
        )
        st.error(
            "❌ CSS próprio com classes próprias é aceitável. O que **quebra** "
            "é mirar classes internas do Streamlit (`.st-emotion-cache-xxxxx`): "
            "elas mudam a cada versão e o layout se desmonta silenciosamente."
        )

# ==========================================================================
with a3:
    st.header("`st.html` vs. `components.html` vs. `components.iframe`")

    st.markdown(
        """
| Função | Isolamento | JavaScript? |
| --- | --- | --- |
| `st.html` | renderiza no DOM da página | ❌ scripts são removidos |
| `st.components.v1.html` | `<iframe>` isolado | ✅ |
| `st.components.v1.iframe` | `<iframe>` de uma URL externa | ✅ (do site remoto) |
"""
    )

    st.subheader("`st.html` — um alerta customizado")
    n_baixa = int((df.groupby("produto")["satisfacao"].mean() < 3.9).sum())
    st.html(f"""
    <div style="padding:1rem 1.2rem;border-radius:10px;background:#fff1f1;
                border-left:4px solid #ff4b4b">
      <strong>Atenção</strong> — {n_baixa} produtos com satisfação média
      abaixo de 3,9.
    </div>
    """)

    st.subheader("`components.html` — com JavaScript (iframe isolado)")
    components.html(
        """
        <div style="font-family:system-ui;padding:1rem;text-align:center">
          <div id="contador" style="font-size:2.4rem;font-weight:700;
                                    color:#ff4b4b">0</div>
          <button onclick="somar()"
                  style="padding:.5rem 1rem;border-radius:6px;
                         border:1px solid #ff4b4b;background:#fff;
                         color:#ff4b4b;cursor:pointer">+1</button>
          <p style="color:#5d6169;font-size:.85rem">
            Este contador roda em JavaScript, dentro do iframe.<br>
            O Python não sabe o valor dele.
          </p>
        </div>
        <script>
          let n = 0;
          function somar() {
            n += 1;
            document.getElementById("contador").textContent = n;
          }
        </script>
        """,
        height=210,
    )
    st.caption(
        "O iframe é isolado: não herda o CSS da página e não consegue alterar "
        "nada fora dele. Para que o valor volte ao Python, seria preciso um "
        "componente bidirecional feito com a Components API."
    )

    st.subheader("`components.iframe` — conteúdo externo")
    if st.checkbox("Carregar a API reference do Streamlit em um iframe"):
        components.iframe("https://docs.streamlit.io/develop/api-reference",
                          height=420, scrolling=True)

# ==========================================================================
with a4:
    st.header("Componentes da comunidade")

    st.markdown(
        """
| Componente | O que faz | Instalação |
| --- | --- | --- |
| `streamlit-aggrid` | Tabela avançada: agrupamento, pivot, edição | `pip install streamlit-aggrid` |
| `streamlit-option-menu` | Menu lateral estilizado | `pip install streamlit-option-menu` |
| `streamlit-folium` | Mapas Leaflet com retorno de clique | `pip install streamlit-folium` |
| `streamlit-extras` | Utilitários pequenos (cartões, badges) | `pip install streamlit-extras` |
| `streamlit-lottie` | Animações Lottie | `pip install streamlit-lottie` |
| `streamlit-authenticator` | Login com usuário e senha | `pip install streamlit-authenticator` |
"""
    )

    st.code(
        '''from streamlit_option_menu import option_menu

with st.sidebar:
    pagina = option_menu(
        menu_title="Navegação",
        options=["Visão geral", "Regiões", "Produtos"],
        icons=["speedometer2", "map", "box-seam"],
        default_index=0,
        styles={"nav-link-selected": {"background-color": "#1c6fd6"}},
    )''',
        language="python",
    )

    st.warning(
        "⚠️ **Antes de adotar um componente em produção**, verifique: data da "
        "última atualização, issues abertas, compatibilidade com a sua versão "
        "do Streamlit e licença. Um componente abandonado quebra no próximo "
        "upgrade — e o conserto não estará nas suas mãos."
    )

    st.divider()
    st.subheader("Onde procurar")
    l1, l2 = st.columns(2)
    with l1:
        st.link_button("🧩 Components Hub", "https://components.streamlit.app/",
                       use_container_width=True)
        st.link_button("🖼️ App Gallery", "https://streamlit.io/gallery",
                       use_container_width=True)
    with l2:
        st.link_button("📚 Documentação", "https://docs.streamlit.io",
                       use_container_width=True)
        st.link_button("💬 Fórum", "https://discuss.streamlit.io",
                       use_container_width=True)
