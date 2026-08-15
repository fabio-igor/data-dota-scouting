import json
import os

import duckdb

conexao = duckdb.connect("data/processed/scouting_platform.duckdb")

conexao.execute("DROP TABLE IF EXISTS economia_10min")
conexao.execute("""
    CREATE TABLE economia_10min (
        match_id BIGINT,
        account_id BIGINT,
        gold_aos_10min INTEGER,
        xp_aos_10min INTEGER,
        PRIMARY KEY (match_id, account_id)
    )
""")

pasta_detalhes = "data/raw/match_details"
total_inseridos = 0
sem_dado_10min = 0

for nome_arquivo in os.listdir(pasta_detalhes):
    caminho = os.path.join(pasta_detalhes, nome_arquivo)

    with open(caminho, "r", encoding="utf-8") as arquivo:
        detalhes = json.load(arquivo)

    match_id = detalhes["match_id"]

    for jogador in detalhes["players"]:
        account_id = jogador.get("account_id")
        if account_id is None:
            continue

        gold_t = jogador.get("gold_t")
        xp_t = jogador.get("xp_t")

        if not gold_t or len(gold_t) <= 10:
            sem_dado_10min += 1
            continue

        conexao.execute(
            """
            INSERT OR REPLACE INTO economia_10min
            (match_id, account_id, gold_aos_10min, xp_aos_10min)
            VALUES (?, ?, ?, ?)
        """,
            (match_id, account_id, gold_t[10], xp_t[10] if xp_t else None),
        )
        total_inseridos += 1

conexao.close()

print(f"{total_inseridos} registros inseridos.")
print(f"{sem_dado_10min} registros sem dado suficiente aos 10min.")
