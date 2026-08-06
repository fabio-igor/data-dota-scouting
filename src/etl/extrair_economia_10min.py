import json
import os
import sqlite3

conexao = sqlite3.connect("data/processed/lgd_scouting.db")
cursor = conexao.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS economia_10min (
        match_id INTEGER,
        account_id INTEGER,
        gold_aos_10min INTEGER,
        xp_aos_10min INTEGER,
        PRIMARY KEY (match_id, account_id)
    )
""")

jogadores_lgd = {177203952, 292921272, 1026694469, 105045291, 81306398}
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
        if account_id not in jogadores_lgd:
            continue

        gold_t = jogador.get("gold_t")
        xp_t = jogador.get("xp_t")

        # Confere se a partida durou pelo menos 10 minutos de dado registrado
        if not gold_t or len(gold_t) <= 10:
            sem_dado_10min += 1
            continue

        cursor.execute(
            """
            INSERT OR REPLACE INTO economia_10min
            (match_id, account_id, gold_aos_10min, xp_aos_10min)
            VALUES (?, ?, ?, ?)
        """,
            (match_id, account_id, gold_t[10], xp_t[10] if xp_t else None),
        )
        total_inseridos += 1

conexao.commit()
conexao.close()

print(f"{total_inseridos} registros inseridos.")
print(f"{sem_dado_10min} registros sem dado suficiente aos 10min.")
