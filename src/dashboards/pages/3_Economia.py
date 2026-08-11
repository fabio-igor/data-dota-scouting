import sqlite3

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Economia — LGD", layout="wide")
st.title("Economia")


@st.cache_data
def carregar_curva_economia():
    conexao = sqlite3.connect("data/processed/lgd_scouting.db")

    # Soma dos 5 jogadores da LGD, por minuto, separado por vitória/derrota da partida.
    # Antes esse dado vinha de reparsear os 62 JSONs brutos (33 MB) a cada rerun
    # do Streamlit; agora vem direto da tabela pré-agregada pelo ETL.
    query = """
        SELECT
            epm.minuto AS Minuto,
            p.lgd_radiant = p.radiant_win AS vitoria,
            SUM(epm.gold) AS gold_time
        FROM economia_por_minuto epm
        JOIN partidas p ON epm.match_id = p.match_id
        WHERE epm.minuto <= 40
        GROUP BY epm.minuto, p.match_id, vitoria
    """
    df_bruto = pd.read_sql_query(query, conexao)
    conexao.close()

    # Média entre partidas, por minuto, separando vitórias e derrotas
    medias = (
        df_bruto.groupby(["Minuto", "vitoria"])["gold_time"]
        .mean()
        .unstack("vitoria")
        .rename(columns={True: "Vitórias", False: "Derrotas"})
    )
    return medias


df = carregar_curva_economia()

st.subheader("Economia do time (soma dos 5 jogadores) — Vitórias vs. Derrotas")
st.line_chart(df, color=["#e74c3c", "#2ecc71"])

st.markdown("""
**Leitura**: aos 10 minutos, a diferença entre vitórias e derrotas é de apenas ~9%.
Ela cresce de forma gradual ao longo da partida, chegando a ~13% por volta dos
27-30 minutos e permanecendo nessa faixa até o fim. É um crescimento consistente,
não um salto concentrado em uma fase — os dados não indicam claramente em qual
momento do jogo a vantagem da LGD é decidida.
""")
