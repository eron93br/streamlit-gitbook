---
title: "11. Cache e performance"
subject: "Parte 4: Interatividade"
---

# Cache e performance

:::{admonition} O que você vai aprender
:class: tip
- Por que o modelo de rerun torna o cache **obrigatório**, não opcional
- A diferença entre `st.cache_data` e `st.cache_resource`
- Como o Streamlit decide se um resultado está em cache (a chave de hash)
- `ttl`, `max_entries`, `show_spinner` e como invalidar o cache
- Erros clássicos: mutação do objeto cacheado, argumentos não-hasheáveis
- Um checklist de desempenho para dashboards
:::

:::{div}
:class: run-quick
**Rode este código:** [`part4/labs/ch11_lab.py`](./labs/ch11_lab.py) — mede o
tempo da mesma operação com e sem cache, na sua frente.
`streamlit run part4/labs/ch11_lab.py`
:::

:::{div}
:class: api-ref
🔗 **Referência da API:** [Caching](https://docs.streamlit.io/develop/api-reference/caching-and-state)
· [`st.cache_data`](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_data)
· [`st.cache_resource`](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_resource)
:::

## Visão geral

### Por que o cache é obrigatório

O script inteiro roda a cada interação. Sem cache, um `pd.read_csv` de 200 MB no
topo do arquivo é relido toda vez que alguém arrasta um slider. Com cinco
filtros, o usuário provoca cinco leituras completas do disco para montar uma
única consulta.

O cache quebra esse ciclo: a função executa **uma vez**, e nos reruns seguintes o
resultado é devolvido da memória.

```python
@st.cache_data
def carregar(caminho: str) -> pd.DataFrame:
    return pd.read_csv(caminho, parse_dates=["data"])

df = carregar("data/vendas.csv")     # lento só na primeira vez
```

### `cache_data` vs. `cache_resource`

Esta é a distinção que gera mais dúvida, e a regra é simples.

| | `st.cache_data` | `st.cache_resource` |
| --- | --- | --- |
| **Para** | Dados: DataFrames, listas, dicts, arrays, strings | Recursos: conexões, modelos de ML, clientes de API |
| **O que armazena** | Uma **cópia serializada** do retorno | O **próprio objeto**, compartilhado |
| **Cada chamada devolve** | Uma cópia nova | A mesma instância |
| **Mutar o retorno afeta o cache?** | Não | **Sim** |
| **Exemplo** | `carregar_csv()`, `agregar()`, `consultar_api()` | `conectar_banco()`, `carregar_modelo()` |

:::{admonition} A regra de bolso
:class: tip
**Se o objeto pode ser serializado e você quer uma cópia → `cache_data`.**
**Se o objeto não deve (ou não pode) ser copiado → `cache_resource`.**

Uma conexão com banco não pode ser copiada — copiá-la abriria uma nova conexão a
cada rerun, esgotando o pool. Um DataFrame pode, e deve, para que um usuário não
altere o dado que outro vai ler.
:::

```python
@st.cache_data(ttl="1h")
def consultar_vendas(data_inicio, data_fim) -> pd.DataFrame:
    return pd.read_sql(query, conexao(), params=(data_inicio, data_fim))

@st.cache_resource
def conexao():
    return create_engine(st.secrets["db"]["url"])
```

### Como o Streamlit decide se há acerto de cache

A chave é composta por:

1. o **corpo da função** (mudou o código → cache invalidado);
2. o **nome** da função;
3. os **valores dos argumentos**, hasheados.

```python
carregar("data/vendas.csv")   # executa
carregar("data/vendas.csv")   # cache hit
carregar("data/outro.csv")    # executa (argumento diferente)
```

:::{admonition} Argumentos que o Streamlit não consegue hashear
:class: warning
Conexões, sockets, objetos customizados sem `__hash__` levantam
`UnhashableParamError`. Duas saídas:

**1. Prefixe o parâmetro com `_`** — o Streamlit o ignora ao montar a chave:

```python
@st.cache_data
def consultar(_conexao, data_inicio, data_fim):
    return pd.read_sql(query, _conexao, params=(data_inicio, data_fim))
```

**2. Use `hash_funcs`** para ensinar o Streamlit a hashear aquele tipo.

⚠️ Ao ignorar um parâmetro com `_`, você assume a responsabilidade: se o objeto
ignorado mudar, o cache **não** perceberá.
:::

### Os argumentos do decorador

| Argumento | Efeito |
| --- | --- |
| `ttl="10m"` / `ttl=600` | Tempo de vida. Essencial para dados que mudam na origem. |
| `max_entries=50` | Limita o número de resultados guardados (evita estourar memória) |
| `show_spinner="Carregando…"` | Texto do spinner exibido durante a execução; `False` desativa |
| `persist="disk"` | Mantém o cache entre reinícios do app (só `cache_data`) |
| `hash_funcs={Tipo: funcao}` | Hash customizado por tipo |

```python
@st.cache_data(ttl="15m", max_entries=20, show_spinner="Consultando base…")
def indicadores(mes: str) -> pd.DataFrame:
    ...
```

### Invalidar o cache

```python
carregar.clear()          # limpa o cache de uma função específica
st.cache_data.clear()     # limpa todo o cache de dados
```

Um botão de atualização manual é uma cortesia que quase todo dashboard
corporativo deveria ter:

```python
if st.sidebar.button("🔄 Atualizar dados"):
    st.cache_data.clear()
    st.rerun()
```

### O erro clássico: mutar o resultado cacheado

```python
@st.cache_data
def carregar():
    return pd.read_csv("data/vendas.csv")

df = carregar()
df["nova_coluna"] = 1        # ⚠️ com cache_data isto é seguro (é uma cópia)
                             # ⚠️ com cache_resource, isto contamina TODAS as sessões
```

Com `cache_data`, cada chamada devolve uma cópia — mutar é seguro, embora custe
memória. Com `cache_resource`, todos compartilham o mesmo objeto: uma mutação
feita por um usuário é vista por todos os outros. É por isso que DataFrames
pertencem ao `cache_data`.

### Checklist de desempenho

1. **Cacheie a carga de dados.** `@st.cache_data` no `read_csv`/`read_sql`.
2. **Cacheie as agregações caras**, não só a leitura.
3. **Filtre cedo, agregue depois.** Reduza o volume antes do `groupby`.
4. **Não cacheie o que é trivial.** O overhead do hash pode superar o ganho.
5. **Use `st.fragment`** para isolar reruns de painéis pesados
   ([Capítulo 10](./ch10-session-state-e-rerun.md)).
6. **Use `st.form`** para adiar o rerun de filtros múltiplos
   ([Capítulo 9](./ch09-widgets-de-input.md)).
7. **Limite as linhas exibidas.** `st.dataframe(df.head(1000))` em vez da tabela
   inteira.
8. **Prefira formatos colunares.** Parquet lê muito mais rápido que CSV.
9. **Meça antes de otimizar.** `time.perf_counter()` em volta do trecho suspeito.

## Mãos à obra

**Passo 1 — Medir o ganho.**

```python
import time
import streamlit as st
import pandas as pd

def carregar_sem_cache(caminho):
    time.sleep(1.5)                      # simula I/O lento
    return pd.read_csv(caminho, parse_dates=["data"])

@st.cache_data
def carregar_com_cache(caminho):
    time.sleep(1.5)
    return pd.read_csv(caminho, parse_dates=["data"])

col1, col2 = st.columns(2)

with col1:
    t0 = time.perf_counter()
    carregar_sem_cache("data/vendas.csv")
    st.metric("Sem cache", f"{time.perf_counter() - t0:.2f}s")

with col2:
    t0 = time.perf_counter()
    carregar_com_cache("data/vendas.csv")
    st.metric("Com cache", f"{time.perf_counter() - t0:.3f}s")

st.slider("Mexa aqui para forçar um rerun", 0, 100, 50)
```

Mexa no slider algumas vezes. O primeiro número continua em ~1,5 s; o segundo cai
para milissegundos a partir do segundo rerun.

**Passo 2 — Cachear a agregação, não só a leitura.**

```python
@st.cache_data
def carregar(caminho: str) -> pd.DataFrame:
    return pd.read_csv(caminho, parse_dates=["data"])

@st.cache_data
def agregar_mensal(df: pd.DataFrame, metrica: str) -> pd.DataFrame:
    return (
        df.groupby(pd.Grouper(key="data", freq="MS"), as_index=False)[metrica]
          .sum()
    )

df = carregar("data/vendas.csv")
metrica = st.selectbox("Métrica", ["receita", "lucro", "unidades"])
mensal = agregar_mensal(df, metrica)      # cache por métrica
st.line_chart(mensal.set_index("data"))
```

Cada métrica é calculada uma vez e reaproveitada nas trocas seguintes.

**Passo 3 — TTL para dados que mudam na origem.**

```python
@st.cache_data(ttl="10m", show_spinner="Consultando a base…")
def indicadores_do_dia():
    return pd.read_sql("SELECT * FROM vendas WHERE data = CURRENT_DATE", conexao())
```

**Passo 4 — Recurso compartilhado.**

```python
@st.cache_resource
def conexao():
    from sqlalchemy import create_engine
    return create_engine(st.secrets["db"]["url"], pool_pre_ping=True)
```

Uma única engine para todas as sessões, com pool de conexões reutilizado.

**Passo 5 — Botão de atualização.**

```python
with st.sidebar:
    if st.button("🔄 Atualizar dados", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.caption("Os dados são cacheados por 10 minutos.")
```

:::{card} **Vá além**
O laboratório [`ch11_lab.py`](./labs/ch11_lab.py) cronometra cada etapa de um
pipeline e mostra o efeito do cache em cada uma.
:::

## Questões para reflexão

1. O cache troca memória por tempo. Como você estimaria, antes de implementar,
   se essa troca compensa em um dashboard específico?
2. Prefixar um argumento com `_` desliga o hash daquele parâmetro. Descreva um
   bug sutil que isso pode causar e como você o detectaria.
3. `cache_resource` compartilha o mesmo objeto entre todas as sessões. Que
   implicações de segurança e de concorrência isso tem em um app corporativo?
4. Um `ttl` curto mantém os dados frescos e reduz o ganho do cache. Como você
   escolheria o valor para um dashboard operacional versus um dashboard mensal?
5. O checklist recomenda "meça antes de otimizar". Por que essa ordem importa
   especialmente em um framework que reexecuta tudo o tempo todo?

## Teste você mesmo

:::{dropdown} **Q1.** Por que o cache é praticamente obrigatório em apps Streamlit?
**Resposta:** porque o script inteiro é reexecutado a cada interação. Sem cache,
operações caras — leitura de arquivos, consultas a banco, agregações — se repetem
a cada clique, tornando o app inutilizável.
:::

:::{dropdown} **Q2.** Qual a diferença entre `st.cache_data` e `st.cache_resource`?
**Resposta:** `cache_data` guarda uma cópia serializada do retorno e devolve uma
cópia nova a cada chamada — apropriado para DataFrames e outros dados.
`cache_resource` guarda o próprio objeto, compartilhado entre todas as sessões —
apropriado para conexões de banco, clientes de API e modelos de ML, que não devem
ser duplicados.
:::

:::{dropdown} **Q3.** Como o Streamlit determina se pode reaproveitar um resultado do cache?
**Resposta:** pela combinação do nome da função, do corpo (código) da função e do
hash dos valores dos argumentos. Se qualquer um mudar, a função é executada de
novo.
:::

:::{dropdown} **Q4.** O que fazer quando um argumento não pode ser hasheado?
**Resposta:** prefixar o nome do parâmetro com underscore (`_conexao`), o que faz
o Streamlit ignorá-lo na chave do cache; ou fornecer `hash_funcs` ensinando como
hashear aquele tipo. No primeiro caso, mudanças nesse argumento não invalidam o
cache.
:::

:::{dropdown} **Q5.** Como limpar o cache de uma função específica e de todas as funções?
**Resposta:** `minha_funcao.clear()` limpa o cache daquela função;
`st.cache_data.clear()` (ou `st.cache_resource.clear()`) limpa tudo.
:::

:::{dropdown} **Q6.** Por que é perigoso mutar um DataFrame retornado por `st.cache_resource`?
**Resposta:** porque `cache_resource` devolve a **mesma instância** a todas as
sessões. Uma alteração feita por um usuário passa a ser vista por todos os
outros, produzindo resultados incorretos e difíceis de reproduzir. DataFrames
devem usar `cache_data`, que devolve cópias.
:::

---

:::{div}
:class: chapter-footer
[← Capítulo 10](./ch10-session-state-e-rerun.md) · [Índice](../conteudo.md) ·
[Capítulo 12 → Layouts e containers](../part5/ch12-layouts-e-containers.md)
:::
