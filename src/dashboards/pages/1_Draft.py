import sqlite3

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Draft — LGD", layout="wide")
st.title("Draft")

conexao = sqlite3.connect("data/processed/lgd_scouting.db")

# --- Seção 1: Heróis mais pickados pelo time ---
st.header("Heróis mais pickados pela LGD")

query_picks = """
    SELECT herois.nome_localizado as Heroi, COUNT(*) as Vezes
    FROM picks_bans
    JOIN herois ON picks_bans.hero_id = herois.hero_id
    WHERE picks_bans.time_lgd = 1 AND picks_bans.is_pick = 1
    GROUP BY herois.nome_localizado
    ORDER BY Vezes DESC
    LIMIT 10
"""
df_picks = pd.read_sql_query(query_picks, conexao)
st.bar_chart(df_picks.set_index("Heroi"))

# --- Seção 2: Bans específicos por adversário (padrão validado na Etapa 8) ---
st.header("Bans específicos por adversário (confrontos com histórico)")
st.caption(
    "Restrito aos 3 adversários com confrontos suficientes para análise confiável (6+ partidas)."
)

adversarios_relevantes = ["Team Yandex", "BoomBoys", "PlayTime"]
adversario_selecionado = st.selectbox("Escolha o adversário:", adversarios_relevantes)

query_bans_adversario = """
    SELECT herois.nome_localizado as Heroi, COUNT(*) as Vezes
    FROM picks_bans
    JOIN herois ON picks_bans.hero_id = herois.hero_id
    JOIN partidas ON picks_bans.match_id = partidas.match_id
    WHERE picks_bans.time_lgd = 1
      AND picks_bans.is_pick = 0
      AND partidas.opposing_team_name = ?
    GROUP BY herois.nome_localizado
    ORDER BY Vezes DESC
    LIMIT 5
"""
df_bans = pd.read_sql_query(
    query_bans_adversario, conexao, params=(adversario_selecionado,)
)
st.dataframe(df_bans, use_container_width=True)

conexao.close()
