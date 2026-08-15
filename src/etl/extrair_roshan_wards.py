import json
import os

import duckdb

conexao = duckdb.connect("data/processed/scouting_platform.duckdb")

conexao.execute("DROP TABLE IF EXISTS roshan_kills")
conexao.execute("""
    CREATE TABLE roshan_kills (
        match_id BIGINT,
        ordem INTEGER,
        tempo_segundos INTEGER,
        time_id BIGINT,
        PRIMARY KEY (match_id, ordem)
    )
""")

times_por_partida = {
    row[0]: (row[1], row[2])
    for row in conexao.execute(
        "SELECT match_id, radiant_team_id, dire_team_id FROM partidas"
    ).fetchall()
}

pasta_detalhes = "data/raw/match_details"
total_inseridos = 0

for nome_arquivo in os.listdir(pasta_detalhes):
    caminho = os.path.join(pasta_detalhes, nome_arquivo)
    with open(caminho, "r", encoding="utf-8") as arquivo:
        detalhes = json.load(arquivo)

    match_id = detalhes["match_id"]
    if match_id not in times_por_partida:
        continue
    radiant_team_id, dire_team_id = times_por_partida[match_id]

    eventos_roshan = [
        e
        for e in detalhes.get("objectives", [])
        if e["type"] == "CHAT_MESSAGE_ROSHAN_KILL"
    ]
    for ordem, evento in enumerate(eventos_roshan):
        # Nos objectives, team: 2 = radiant, 3 = dire (convenção diferente
        # da usada em picks_bans, que é 0/1 — atenção ao portar essa lógica)
        time_id = radiant_team_id if evento["team"] == 2 else dire_team_id

        conexao.execute(
            """
            INSERT OR REPLACE INTO roshan_kills (match_id, ordem, tempo_segundos, time_id)
            VALUES (?, ?, ?, ?)
        """,
            (match_id, ordem, evento["time"], time_id),
        )
        total_inseridos += 1

print(f"\n{total_inseridos} eventos de Roshan processados.\n")
resultado = conexao.execute("""
    SELECT time_id, COUNT(*) as total, AVG(tempo_segundos) as tempo_medio
    FROM roshan_kills
    GROUP BY time_id
    ORDER BY total DESC
""").fetchall()
for time_id, total, tempo_medio in resultado:
    minutos = tempo_medio / 60
    print(f"  time_id {time_id}: {total} Roshans, tempo médio {minutos:.1f} min")

conexao.close()
