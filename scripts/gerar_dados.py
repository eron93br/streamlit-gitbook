"""Gera o dataset sintético usado em todos os laboratórios deste livro.

Uso:
    python scripts/gerar_dados.py

Saída:
    data/vendas.csv  (~4.000 linhas, 2 anos de vendas diárias)

O dataset é sintético mas não é aleatório puro: ele embute sazonalidade
mensal, um efeito de fim de semana, diferenças reais de margem entre
categorias e um crescimento leve ao longo do tempo. Isso importa — um
dashboard construído sobre ruído branco não ensina nada, porque nenhum
filtro revela padrão algum.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
SAIDA_PADRAO = RAIZ / "data" / "vendas.csv"

REGIOES = {
    "Nordeste": 1.00,
    "Sudeste": 1.45,
    "Sul": 1.10,
    "Centro-Oeste": 0.75,
    "Norte": 0.60,
}

# categoria -> (preço médio, desvio do preço, margem bruta média)
CATEGORIAS = {
    "Eletrônicos": (1850.0, 480.0, 0.18),
    "Vestuário": (159.0, 55.0, 0.52),
    "Casa e Decoração": (320.0, 120.0, 0.41),
    "Alimentos": (48.0, 18.0, 0.26),
    "Esporte e Lazer": (410.0, 150.0, 0.37),
}

PRODUTOS = {
    "Eletrônicos": ["Notebook Aura", "Fone Pulse", "Monitor Vista", "Tablet Nimbus"],
    "Vestuário": ["Camiseta Base", "Jaqueta Norte", "Tênis Passo", "Calça Trilha"],
    "Casa e Decoração": ["Luminária Sol", "Tapete Onda", "Cadeira Foco", "Vaso Raiz"],
    "Alimentos": ["Café Serra", "Granola Cheia", "Azeite Oliva", "Chá Manhã"],
    "Esporte e Lazer": ["Bicicleta Rota", "Halteres Par", "Barraca Cume", "Prancha Maré"],
}

CANAIS = {"E-commerce": 0.52, "Loja física": 0.33, "Marketplace": 0.15}


def gerar(n_linhas: int = 4000, semente: int = 42) -> pd.DataFrame:
    """Constrói o DataFrame de vendas."""
    rng = np.random.default_rng(semente)

    datas = pd.date_range("2024-01-01", "2025-12-31", freq="D")
    data = rng.choice(datas, size=n_linhas)
    data = pd.to_datetime(np.sort(data))

    regiao = rng.choice(
        list(REGIOES), size=n_linhas, p=_normalizar(list(REGIOES.values()))
    )
    categoria = rng.choice(list(CATEGORIAS), size=n_linhas)
    produto = np.array([rng.choice(PRODUTOS[c]) for c in categoria])
    canal = rng.choice(list(CANAIS), size=n_linhas, p=list(CANAIS.values()))

    # --- sazonalidade: pico em novembro/dezembro, vale em fevereiro ---
    mes = data.month.to_numpy()
    fator_sazonal = 1 + 0.35 * np.sin((mes - 3) * np.pi / 6)

    # --- efeito de fim de semana: mais volume, ticket menor ---
    fim_de_semana = data.dayofweek.to_numpy() >= 5
    fator_semana = np.where(fim_de_semana, 1.25, 1.00)

    # --- crescimento leve ao longo do período ---
    dias_corridos = (data - data.min()).days.to_numpy()
    fator_tendencia = 1 + 0.0004 * dias_corridos

    fator_regiao = np.array([REGIOES[r] for r in regiao])

    lam = 2.5 * fator_sazonal * fator_semana * fator_tendencia * fator_regiao
    unidades = rng.poisson(lam=lam) + 1

    preco_medio = np.array([CATEGORIAS[c][0] for c in categoria])
    preco_desvio = np.array([CATEGORIAS[c][1] for c in categoria])
    preco_unitario = np.maximum(
        rng.normal(preco_medio, preco_desvio), preco_medio * 0.35
    ).round(2)

    receita = (unidades * preco_unitario).round(2)

    margem_base = np.array([CATEGORIAS[c][2] for c in categoria])
    # marketplace cobra comissão: margem menor
    ajuste_canal = np.where(canal == "Marketplace", -0.09, 0.0)
    margem = np.clip(rng.normal(margem_base + ajuste_canal, 0.05), 0.02, 0.80)

    custo = (receita * (1 - margem)).round(2)
    lucro = (receita - custo).round(2)

    # satisfação correlacionada (fracamente) com a margem e o canal
    satisfacao = np.clip(
        rng.normal(3.9 + 1.2 * (margem - 0.35), 0.55), 1.0, 5.0
    ).round(1)

    df = pd.DataFrame(
        {
            "data": data,
            "regiao": regiao,
            "categoria": categoria,
            "produto": produto,
            "canal": canal,
            "unidades": unidades,
            "preco_unitario": preco_unitario,
            "receita": receita,
            "custo": custo,
            "lucro": lucro,
            "satisfacao": satisfacao,
        }
    )

    # --- alguns valores ausentes propositais, para exercitar a limpeza ---
    faltantes = rng.choice(df.index, size=int(0.015 * len(df)), replace=False)
    df.loc[faltantes, "satisfacao"] = np.nan

    return df.sort_values("data").reset_index(drop=True)


def _normalizar(pesos: list[float]) -> list[float]:
    total = sum(pesos)
    return [p / total for p in pesos]


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera o dataset de vendas.")
    parser.add_argument("--linhas", type=int, default=4000)
    parser.add_argument("--semente", type=int, default=42)
    parser.add_argument("--saida", type=Path, default=SAIDA_PADRAO)
    args = parser.parse_args()

    df = gerar(args.linhas, args.semente)
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.saida, index=False)

    print(f"✅ {len(df):,} linhas gravadas em {args.saida}".replace(",", "."))
    print(f"   Período: {df['data'].min():%d/%m/%Y} a {df['data'].max():%d/%m/%Y}")
    print(f"   Receita total: R$ {df['receita'].sum():,.2f}")
    print(f"   Colunas: {', '.join(df.columns)}")


if __name__ == "__main__":
    main()
