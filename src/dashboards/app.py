import duckdb
import streamlit as st

LGD_TEAM_ID = 10150538

st.set_page_config(page_title="LGD Scouting Report", layout="wide")


@st.cache_data
def carregar_resumo():
    conexao = duckdb.connect("data/processed/scouting_platform.duckdb")
    partidas_lgd = conexao.execute(
        "SELECT COUNT(*) FROM partidas WHERE radiant_team_id = ? OR dire_team_id = ?",
        [LGD_TEAM_ID, LGD_TEAM_ID],
    ).fetchone()[0]
    total_times = conexao.execute("SELECT COUNT(*) FROM times").fetchone()[0]
    total_partidas = conexao.execute("SELECT COUNT(*) FROM partidas").fetchone()[0]
    conexao.close()
    return partidas_lgd, total_times, total_partidas


partidas_lgd, total_times, total_partidas = carregar_resumo()

st.title("Scout Report — LGD Gaming")
st.markdown(f"""
Análise do roster atual da LGD (pós-maio/2026), baseada em {partidas_lgd} partidas competitivas.

Use o menu lateral para navegar entre as seções:
- **Draft**: picks, bans e padrões por adversário
- **Hero Pool**: heróis de conforto por jogador e por time
- **Economia**: como a LGD costuma vencer (e quando a vantagem aparece)
""")

st.caption(
    f"A base já rastreia {total_times} times e {total_partidas} partidas no total "
    "(incluindo TI2026) — esse dashboard mostra só a LGD por enquanto; "
    "a busca por qualquer time vem na versão web (Fase 4)."
)
