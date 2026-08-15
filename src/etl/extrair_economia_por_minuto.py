import json
import os

import duckdb

conexao = duckdb.connect("data/processed/scouting_platform.duckdb")

conexao.execute("DROP TABLE IF EXISTS economia_por_minuto")
conexao.execute("""
    CREATE TABLE economia_por_minuto (
        match_id BIGINT,
        account_id BIGINT,
        minuto INTEGER,
        gold INTEGER,
        xp INTEGER,
        PRIMARY KEY (match_id, account_id, minuto)
    )
""")

pasta_detalhes = "data/raw/match_details"
total_inseridos = 0
partidas_sem_dado = 0

for nome_arquivo in os.listdir(pasta_detalhes):
    caminho = os.path.join(pasta_detalhes, nome_arquivo)

    with open(caminho, "r", encoding="utf-8") as arquivo:
        detalhes = json.load(arquivo)

    match_id = detalhes["match_id"]
    encontrou_dado = False

    for jogador in detalhes["players"]:
        account_id = jogador.get("account_id")
        if account_id is None:
            continue

        gold_t = jogador.get("gold_t")
        xp_t = jogador.get("xp_t")
        if not gold_t:
            continue

        encontrou_dado = True
        for minuto, gold in enumerate(gold_t):
            xp = xp_t[minuto] if xp_t and minuto < len(xp_t) else None
            conexao.execute(
                """
                INSERT OR REPLACE INTO economia_por_minuto
                (match_id, account_id, minuto, gold, xp)
                VALUES (?, ?, ?, ?, ?)
            """,
                (match_id, account_id, minuto, gold, xp),
            )
            total_inseridos += 1

    if not encontrou_dado:
        partidas_sem_dado += 1

conexao.close()

print(f"{total_inseridos} registros inseridos em 'economia_por_minuto'.")
print(f"{partidas_sem_dado} partidas sem dado de gold_t.")
