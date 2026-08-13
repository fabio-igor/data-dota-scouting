import duckdb
import streamlit as st

LGD_TEAM_ID = 10150538

st.set_page_config(page_title="Economia — LGD", layout="wide")
st.title("Economia")


@st.cache_data
def carregar_curva_economia():
    conexao = duckdb.connect("data/processed/scouting_platform.duckdb")

    # Soma dos jogadores da LGD (filtrado via jogadores_partida.time_id —
    # necessário desde que a tabela passou a ter os dois times por partida,
    # não só a LGD), por minuto, separado por vitória/derrota.
    query = """
        SELECT
            epm.minuto AS Minuto,
            (jp.time_id = p.radiant_team_id AND p.radiant_win)
              OR (jp.time_id = p.dire_team_id AND NOT p.radiant_win) AS vitoria,
            SUM(epm.gold) AS gold_time
        FROM economia_por_minuto epm
        JOIN jogadores_partida jp
          ON epm.match_id = jp.match_id AND epm.account_id = jp.account_id
        JOIN partidas p ON epm.match_id = p.match_id
        WHERE epm.minuto <= 40 AND jp.time_id = ?
        GROUP BY epm.minuto, p.match_id, vitoria
    """
    df_bruto = conexao.execute(query, [LGD_TEAM_ID]).fetchdf()
    conexao.close()

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
