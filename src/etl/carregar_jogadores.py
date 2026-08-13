import json
import os

import duckdb

conexao = duckdb.connect("data/processed/scouting_platform.duckdb")

conexao.execute("DROP TABLE IF EXISTS jogadores_partida")
conexao.execute("""
    CREATE TABLE jogadores_partida (
        match_id BIGINT,
        account_id BIGINT,
        time_id BIGINT,
        hero_id INTEGER,
        kills INTEGER,
        deaths INTEGER,
        assists INTEGER,
        gpm INTEGER,
        xpm INTEGER,
        PRIMARY KEY (match_id, account_id)
    )
""")

# time_id de cada partida (radiant/dire), pra combinar com isRadiant de cada
# jogador — assim sabemos de qual time é cada jogador sem depender de uma
# lista fixa de roster (funciona pra qualquer jogador, de qualquer time).
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

    for jogador in detalhes["players"]:
        account_id = jogador.get("account_id")
        if account_id is None:
            continue  # perfil privado na Steam, API não devolve o account_id

        time_id = radiant_team_id if jogador["isRadiant"] else dire_team_id

        conexao.execute(
            """
            INSERT OR REPLACE INTO jogadores_partida
            (match_id, account_id, time_id, hero_id, kills, deaths, assists, gpm, xpm)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                match_id,
                account_id,
                time_id,
                jogador["hero_id"],
                jogador["kills"],
                jogador["deaths"],
                jogador["assists"],
                jogador["gold_per_min"],
                jogador["xp_per_min"],
            ),
        )
        total_inseridos += 1

conexao.close()

print(f"{total_inseridos} registros inseridos em 'jogadores_partida'.")
