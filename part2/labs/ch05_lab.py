"""Laboratório 05 — Galeria de elementos de texto e status.

Todos os elementos do Capítulo 5, com o código de cada um ao lado.

Execute na raiz do repositório:
    streamlit run part2/labs/ch05_lab.py
"""

import time
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Lab 05 · Texto e status", page_icon="🔤",
                   layout="wide")

RAIZ = Path(__file__).resolve().parents[2]
CSV = RAIZ / "data" / "vendas.csv"

st.title("🔤 Lab 05 — Elementos de texto e status")
st.caption("Galeria navegável · cada seção mostra o resultado e o código.")
st.divider()

aba_txt, aba_md, aba_status, aba_prog, aba_kpi = st.tabs(
    ["Títulos", "Markdown", "Mensagens", "Progresso", "Aplicação"]
)

# ==========================================================================
with aba_txt:
    st.header("Hierarquia de títulos")

    esq, dir_ = st.columns(2, gap="large")

    with esq:
        st.title("st.title — h1")
        st.header("st.header — h2")
        st.subheader("st.subheader — h3")
        st.markdown("**st.markdown** — livre")
        st.caption("st.caption — nota de rodapé, fonte, data")
        st.text("st.text — literal, **sem** markdown")
        st.divider()
        st.latex(r"\text{margem} = \frac{\text{receita} - \text{custo}}{\text{receita}}")

    with dir_:
        st.code(
            '''st.title("st.title — h1")
st.header("st.header — h2")
st.subheader("st.subheader — h3")
st.markdown("**st.markdown** — livre")
st.caption("st.caption — nota de rodapé")
st.text("st.text — literal, sem markdown")
st.divider()
st.latex(r"\\text{margem} = \\frac{r - c}{r}")''',
            language="python",
            line_numbers=True,
        )
        st.info(
            "Todas as funções de título aceitam `help=` (tooltip) e "
            "`anchor=` (link direto para a seção)."
        )

# ==========================================================================
with aba_md:
    st.header("O markdown estendido do Streamlit")

    esq, dir_ = st.columns(2, gap="large")

    with esq:
        st.subheader("Cores")
        st.markdown(
            "Estados: :green[dentro da meta] · :orange[atenção] · "
            ":red[crítico] · :blue[informativo] · :violet[destaque] · "
            ":gray[secundário]"
        )
        st.markdown("Com fundo: :green-background[aprovado] "
                    ":red-background[reprovado]")

        st.subheader("Badges")
        b1, b2, b3 = st.columns(3)
        b1.badge("Em dia", color="green")
        b2.badge("Atenção", color="orange")
        b3.badge("Atrasado", color="red")

        st.subheader("Emojis")
        st.markdown(
            "Crescimento :chart_with_upwards_trend: · "
            "Alerta :warning: · Concluído :white_check_mark:"
        )

        st.subheader("Código")
        st.code(
            'df.groupby("regiao")["receita"].sum()',
            language="python",
        )

    with dir_:
        st.code(
            '''st.markdown(":green[dentro da meta] · :red[crítico]")
st.markdown(":green-background[aprovado]")

st.badge("Em dia", color="green")

st.markdown("Crescimento :chart_with_upwards_trend:")

st.code('df.groupby("regiao")["receita"].sum()',
        language="python")''',
            language="python",
            line_numbers=True,
        )
        st.warning(
            "⚠️ Cor não deve ser o **único** canal de informação: use também "
            "um ícone ou o texto, para leitores daltônicos."
        )

# ==========================================================================
with aba_status:
    st.header("As cinco mensagens de status")

    st.success("st.success — operação concluída, meta atingida.")
    st.info("st.info — contexto neutro, dica de uso.")
    st.warning("st.warning — dado incompleto, filtro muito restritivo.")
    st.error("st.error — falha que impede o app de continuar.")

    with st.expander("st.exception — só em desenvolvimento"):
        st.exception(ValueError("Exemplo de traceback exibido na interface."))
        st.caption(
            "Em produção, prefira `st.error` com mensagem tratada e registre "
            "o traceback em log — o traceback expõe estrutura interna."
        )

    st.divider()
    st.code(
        '''st.success("Concluído")
st.info("Contexto")
st.warning("Atenção")
st.error("Falha")
st.exception(erro)   # apenas em desenvolvimento''',
        language="python",
    )

# ==========================================================================
with aba_prog:
    st.header("Indicadores de progresso")

    c1, c2 = st.columns(2, gap="large")

    with c1:
        if st.button("▶️ st.spinner (indeterminado)"):
            with st.spinner("Carregando dados…"):
                time.sleep(1.5)
            st.success("Pronto.")

        if st.button("▶️ st.progress (determinado)"):
            barra = st.progress(0, text="Processando regiões…")
            regioes = ["Nordeste", "Sudeste", "Sul", "Centro-Oeste", "Norte"]
            for i, r in enumerate(regioes, start=1):
                time.sleep(0.35)
                barra.progress(i / len(regioes), text=f"Processando {r}…")
            barra.empty()
            st.success("5 regiões processadas.")

    with c2:
        if st.button("▶️ st.status (multietapas)"):
            with st.status("Executando pipeline", expanded=True) as s:
                st.write("Lendo CSV…")
                time.sleep(0.6)
                st.write("Agregando por categoria…")
                time.sleep(0.7)
                st.write("Validando esquema…")
                time.sleep(0.4)
                s.update(label="Pipeline concluído", state="complete",
                         expanded=False)
            st.toast("Relatório atualizado", icon="✅")

        if st.button("🎈 st.balloons"):
            st.balloons()

# ==========================================================================
with aba_kpi:
    st.header("Aplicação: semaforizar um indicador")

    if not CSV.exists():
        st.error("Rode `python scripts/gerar_dados.py` na raiz do repositório.")
        st.stop()

    df = pd.read_csv(CSV, parse_dates=["data"])
    receita = df["receita"].sum()

    meta = st.slider(
        "Meta de receita (R$ milhões)", 5.0, 15.0, 9.0, step=0.5,
        help="Mova para ver o indicador mudar de estado.",
    ) * 1_000_000

    atingimento = receita / meta

    if atingimento >= 1:
        st.markdown(f"### Receita: :green[R$ {receita:,.0f}] :white_check_mark:")
        st.success(f"Meta superada em {atingimento - 1:.1%}.")
    elif atingimento >= 0.9:
        st.markdown(f"### Receita: :orange[R$ {receita:,.0f}] :warning:")
        st.warning(f"Faltam {1 - atingimento:.1%} para a meta.")
    else:
        st.markdown(f"### Receita: :red[R$ {receita:,.0f}] :arrow_down:")
        st.error(f"Abaixo da meta em {1 - atingimento:.1%}.")

    st.progress(min(atingimento, 1.0), text=f"Atingimento: {atingimento:.1%}")

    with st.expander("📖 Como calculamos"):
        st.latex(r"\text{atingimento} = \frac{\sum \text{receita}}{\text{meta}}")
        st.code(
            'atingimento = df["receita"].sum() / meta',
            language="python",
        )
        st.caption("Custos indiretos não estão incluídos na receita.")

    st.info(
        "**O padrão:** a cor comunica o estado, a mensagem explica o porquê. "
        "Um sem o outro é decoração ou parede de texto."
    )
