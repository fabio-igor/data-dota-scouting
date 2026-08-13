import duckdb
import pandas as pd
import streamlit as st

LGD_TEAM_ID = 10150538

st.set_page_config(page_title="Draft — LGD", layout="wide")
st.title("Draft")


@st.cache_data
def carregar_picks_mais_usados():
    conexao = duckdb.connect("data/processed/scouting_platform.duckdb")
    query = """
        SELECT herois.nome_localizado as Heroi, COUNT(*) as Vezes
        FROM picks_bans
        JOIN herois ON picks_bans.hero_id = herois.hero_id
        WHERE picks_bans.time_id = ? AND picks_bans.is_pick = TRUE
        GROUP BY herois.nome_localizado
        ORDER BY Vezes DESC
        LIMIT 10
    """
    df = conexao.execute(query, [LGD_TEAM_ID]).fetchdf()
    conexao.close()
    return df


@st.cache_data
def carregar_adversarios_com_historico(minimo_partidas=6):
    conexao = duckdb.connect("data/processed/scouting_platform.duckdb")
    query = """
        SELECT t.nome, COUNT(*) as partidas
        FROM partidas p
        JOIN times t ON t.time_id = CASE
            WHEN p.radiant_team_id = ? THEN p.dire_team_id
            ELSE p.radiant_team_id
        END
        WHERE p.radiant_team_id = ? OR p.dire_team_id = ?
        GROUP BY t.nome
        HAVING COUNT(*) >= ?
        ORDER BY partidas DESC
    """
    df = conexao.execute(query, [LGD_TEAM_ID, LGD_TEAM_ID, LGD_TEAM_ID, minimo_partidas]).fetchdf()
    conexao.close()
    return df["nome"].tolist()


@st.cache_data
def carregar_bans_por_adversario(nome_adversario):
    conexao = duckdb.connect("data/processed/scouting_platform.duckdb")
    query = """
        SELECT herois.nome_localizado as Heroi, COUNT(*) as Vezes
        FROM picks_bans pb
        JOIN herois ON pb.hero_id = herois.hero_id
        JOIN partidas p ON pb.match_id = p.match_id
        JOIN times t ON t.nome = ?
        WHERE pb.time_id = ?
          AND pb.is_pick = FALSE
          AND (p.radiant_team_id = t.time_id OR p.dire_team_id = t.time_id)
        GROUP BY herois.nome_localizado
        ORDER BY Vezes DESC
        LIMIT 5
    """
    df = conexao.execute(query, [nome_adversario, LGD_TEAM_ID]).fetchdf()
    conexao.close()
    return df


# --- Seção 1: Heróis mais pickados pelo time ---
st.header("Heróis mais pickados pela LGD")
df_picks = carregar_picks_mais_usados()
st.bar_chart(df_picks.set_index("Heroi"))

# --- Seção 2: Bans específicos por adversário ---
st.header("Bans específicos por adversário (confrontos com histórico)")
st.caption("Times com 6+ partidas contra a LGD — lista gerada automaticamente do banco.")

adversarios_relevantes = carregar_adversarios_com_historico()

if adversarios_relevantes:
    adversario_selecionado = st.selectbox("Escolha o adversário:", adversarios_relevantes)
    df_bans = carregar_bans_por_adversario(adversario_selecionado)
    st.dataframe(df_bans, use_container_width=True)
else:
    st.info("Nenhum adversário ainda tem 6+ partidas registradas contra a LGD.")
