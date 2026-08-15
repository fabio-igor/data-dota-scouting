import json
import os

import duckdb

conexao = duckdb.connect("data/processed/scouting_platform.duckdb")

conexao.execute("DROP TABLE IF EXISTS picks_bans")
conexao.execute("""
    CREATE TABLE picks_bans (
        match_id BIGINT,
        ordem INTEGER,
        hero_id INTEGER,
        is_pick BOOLEAN,
        time_id BIGINT,
        PRIMARY KEY (match_id, ordem)
    )
""")

# time_id de cada partida (radiant/dire) — mesma lógica de carregar_jogadores.py
times_por_partida = {
    row[0]: (row[1], row[2])
    for row in conexao.execute(
        "SELECT match_id, radiant_team_id, dire_team_id FROM partidas"
    ).fetchall()
}

pasta_detalhes = "data/raw/match_details"
total_inseridos = 0
partidas_sem_draft = 0

for nome_arquivo in os.listdir(pasta_detalhes):
    caminho = os.path.join(pasta_detalhes, nome_arquivo)

    with open(caminho, "r", encoding="utf-8") as arquivo:
        detalhes = json.load(arquivo)

    match_id = detalhes["match_id"]
    picks_bans = detalhes.get("picks_bans")

    if not picks_bans or match_id not in times_por_partida:
        partidas_sem_draft += 1
        continue

    radiant_team_id, dire_team_id = times_por_partida[match_id]

    for evento in picks_bans:
        # No formato da OpenDota, team=0 é o lado Radiant, team=1 é Dire
        time_id = radiant_team_id if evento["team"] == 0 else dire_team_id

        conexao.execute(
            """
            INSERT OR REPLACE INTO picks_bans
            (match_id, ordem, hero_id, is_pick, time_id)
            VALUES (?, ?, ?, ?, ?)
        """,
            (match_id, evento["order"], evento["hero_id"], evento["is_pick"], time_id),
        )
        total_inseridos += 1

conexao.close()

print(f"{total_inseridos} eventos de draft inseridos.")
print(f"{partidas_sem_draft} partidas sem dado de draft disponível.")
