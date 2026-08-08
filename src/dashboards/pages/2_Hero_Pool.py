import sqlite3

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Hero Pool — LGD", layout="wide")
st.title("Hero Pool")

conexao = sqlite3.connect("data/processed/lgd_scouting.db")

nomes_jogadores = {
    177203952: "Yuma",
    292921272: "Wisper",
    1026694469: "TaiLung",
    105045291: "Thiolicor",
    81306398: "KJ",
}

jogador_nome = st.selectbox("Escolha o jogador:", list(nomes_jogadores.values()))
account_id = [aid for aid, nome in nomes_jogadores.items() if nome == jogador_nome][0]

query = """
    SELECT herois.nome_localizado as Heroi,
           COUNT(*) as Partidas,
           SUM(CASE WHEN partidas.lgd_radiant = partidas.radiant_win THEN 1 ELSE 0 END) as Vitorias
    FROM jogadores_partida
    JOIN herois ON jogadores_partida.hero_id = herois.hero_id
    JOIN partidas ON jogadores_partida.match_id = partidas.match_id
    WHERE jogadores_partida.account_id = ?
    GROUP BY herois.nome_localizado
    HAVING Partidas >= 2
    ORDER BY Partidas DESC, Vitorias DESC
    LIMIT 5
"""
df = pd.read_sql_query(query, conexao, params=(account_id,))
df["Winrate (%)"] = (df["Vitorias"] / df["Partidas"] * 100).round(0)

st.subheader(f"Top heróis de {jogador_nome}")
st.dataframe(df, use_container_width=True, hide_index=True)

conexao.close()
