"""
Migração do schema single-team (LGD) para multi-time.

Decisão de design (explicada em detalhe na conversa com o mentor):
- lgd_radiant / time_lgd (booleanos) viram radiant_team_id / dire_team_id
  (ou time_id, quando é por linha de jogador/pick/ban) — usando os dois
  lados reais do Dota (Radiant/Dire) em vez de "meu time vs adversário".
- Isso elimina a necessidade de um roster.py por time: quem jogou por
  quem, em cada partida, já vem no dado bruto da API (campo isRadiant).
- O roster.py que fizemos pra LGD continua útil, mas pra outra coisa:
  mostrar o roster ATUAL de um time numa tela, não pra reconstruir
  histórico (isso é o que os dados de partida já garantem).

LGD_TEAM_ID = 10150538 (o único ID de time que conhecemos por enquanto —
os adversários ainda estão só como texto em opposing_team_name; resolver
os IDs deles é um passo futuro, quando formos coletar dados deles também).
"""

import duckdb

LGD_TEAM_ID = 10150538
CAMINHO_ANTIGO = "data/processed/lgd_scouting.duckdb"
CAMINHO_NOVO = "data/processed/scouting_platform.duckdb"

con_antigo = duckdb.connect(CAMINHO_ANTIGO)
con_novo = duckdb.connect(CAMINHO_NOVO)

# --- 1. Tabela nova: times (dimensão) ---
con_novo.execute("""
    CREATE OR REPLACE TABLE times (
        time_id BIGINT PRIMARY KEY,
        nome VARCHAR,
        tier VARCHAR,
        regiao VARCHAR
    )
""")
con_novo.execute("""
    INSERT INTO times VALUES (?, 'LGD Gaming', '1', 'SA')
""", [LGD_TEAM_ID])
print("times: 1 registro (LGD Gaming) inserido — adversários entram quando coletarmos os IDs deles")

# --- 2. partidas: lgd_radiant/lgd_score/adversario_score -> radiant/dire genérico ---
df_partidas = con_antigo.execute("SELECT * FROM partidas").fetchdf()
df_partidas["radiant_team_id"] = df_partidas["lgd_radiant"].apply(
    lambda lgd_e_radiant: LGD_TEAM_ID if lgd_e_radiant else None
)
df_partidas["dire_team_id"] = df_partidas["lgd_radiant"].apply(
    lambda lgd_e_radiant: None if lgd_e_radiant else LGD_TEAM_ID
)
df_partidas["radiant_score"] = df_partidas.apply(
    lambda linha: linha["lgd_score"] if linha["lgd_radiant"] else linha["adversario_score"], axis=1
)
df_partidas["dire_score"] = df_partidas.apply(
    lambda linha: linha["adversario_score"] if linha["lgd_radiant"] else linha["lgd_score"], axis=1
)
df_partidas_novo = df_partidas[[
    "match_id", "radiant_team_id", "dire_team_id", "radiant_win",
    "radiant_score", "dire_score", "duration", "start_time",
    "league_name", "opposing_team_name",
]]
con_novo.execute("CREATE OR REPLACE TABLE partidas AS SELECT * FROM df_partidas_novo")
print(f"partidas: {len(df_partidas_novo)} linhas migradas")

# --- 3. jogadores_partida: adiciona time_id (hoje só tem jogador da LGD) ---
df_jp = con_antigo.execute("SELECT * FROM jogadores_partida").fetchdf()
df_jp["time_id"] = LGD_TEAM_ID
con_novo.execute("CREATE OR REPLACE TABLE jogadores_partida AS SELECT * FROM df_jp")
print(f"jogadores_partida: {len(df_jp)} linhas migradas")

# --- 4. picks_bans: time_lgd (bool) -> time_id ---
df_pb = con_antigo.execute("SELECT * FROM picks_bans").fetchdf()
df_pb["time_id"] = df_pb["time_lgd"].apply(lambda e_lgd: LGD_TEAM_ID if e_lgd else None)
df_pb_novo = df_pb[["match_id", "ordem", "hero_id", "is_pick", "time_id"]]
con_novo.execute("CREATE OR REPLACE TABLE picks_bans AS SELECT * FROM df_pb_novo")
print(f"picks_bans: {len(df_pb_novo)} linhas migradas")

# --- 5. roshan_kills: time_lgd (bool) -> time_id ---
df_rk = con_antigo.execute("SELECT * FROM roshan_kills").fetchdf()
df_rk["time_id"] = df_rk["time_lgd"].apply(lambda e_lgd: LGD_TEAM_ID if e_lgd else None)
df_rk_novo = df_rk[["match_id", "ordem", "tempo_segundos", "time_id"]]
con_novo.execute("CREATE OR REPLACE TABLE roshan_kills AS SELECT * FROM df_rk_novo")
print(f"roshan_kills: {len(df_rk_novo)} linhas migradas")

# --- 6. Tabelas que já eram genéricas (match_id/account_id) — copia direto ---
for tabela in ["herois", "economia_10min", "economia_por_minuto", "wards_por_jogador"]:
    df = con_antigo.execute(f"SELECT * FROM {tabela}").fetchdf()
    con_novo.execute(f"CREATE OR REPLACE TABLE {tabela} AS SELECT * FROM df")
    print(f"{tabela}: {len(df)} linhas copiadas (schema já era genérico)")

con_antigo.close()
con_novo.close()

print(f"\nMigração concluída. Banco multi-time salvo em: {CAMINHO_NOVO}")
print("O banco antigo (lgd_scouting.duckdb) continua intacto, como backup.")
