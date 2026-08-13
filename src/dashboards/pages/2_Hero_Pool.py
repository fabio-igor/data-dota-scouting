import os
import sys

import duckdb
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from src.config.roster import ROSTER

st.set_page_config(page_title="Hero Pool — LGD", layout="wide")
st.title("Hero Pool")

# Inclui jogadores que já saíram (ex: TaiLung) marcados como "(saiu)",
# pra permitir consultar o hero pool histórico deles também.
nomes_jogadores = {
    j["account_id"]: (j["nome"] if j["data_saida"] is None else f"{j['nome']} (saiu)")
    for j in ROSTER
}


@st.cache_data
def carregar_top_herois(account_id):
    conexao = duckdb.connect("data/processed/scouting_platform.duckdb")
    query = """
        SELECT herois.nome_localizado as Heroi,
               COUNT(*) as Partidas,
               SUM(CASE
                   WHEN jp.time_id = p.radiant_team_id AND p.radiant_win THEN 1
                   WHEN jp.time_id = p.dire_team_id AND NOT p.radiant_win THEN 1
                   ELSE 0
               END) as Vitorias
        FROM jogadores_partida jp
        JOIN herois ON jp.hero_id = herois.hero_id
        JOIN partidas p ON jp.match_id = p.match_id
        WHERE jp.account_id = ?
        GROUP BY herois.nome_localizado
        HAVING Partidas >= 2
        ORDER BY Partidas DESC, Vitorias DESC
        LIMIT 5
    """
    df = conexao.execute(query, [account_id]).fetchdf()
    conexao.close()
    df["Winrate (%)"] = (df["Vitorias"] / df["Partidas"] * 100).round(0)
    return df


jogador_nome = st.selectbox("Escolha o jogador:", list(nomes_jogadores.values()))
account_id = [aid for aid, nome in nomes_jogadores.items() if nome == jogador_nome][0]

df = carregar_top_herois(account_id)

st.subheader(f"Top heróis de {jogador_nome}")
st.dataframe(df, use_container_width=True, hide_index=True)
