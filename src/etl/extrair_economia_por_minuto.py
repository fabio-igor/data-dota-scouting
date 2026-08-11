import json
import os
import sqlite3
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.config.roster import todos_ids_historicos


conexao = sqlite3.connect("data/processed/lgd_scouting.db")
cursor = conexao.cursor()

# Formato "tidy": uma linha por (partida, jogador, minuto).
# Fica fácil de agregar em SQL (soma do time por minuto, filtro por faixa
# de tempo, join com 'partidas') e migra direto pra Parquet/DuckDB depois.
cursor.execute("""
    CREATE TABLE IF NOT EXISTS economia_por_minuto (
        match_id INTEGER,
        account_id INTEGER,
        minuto INTEGER,
        gold INTEGER,
        xp INTEGER,
        PRIMARY KEY (match_id, account_id, minuto)
    )
""")

jogadores_lgd = todos_ids_historicos()  # importado de src/config/roster.py
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
        if account_id not in jogadores_lgd:
            continue

        gold_t = jogador.get("gold_t")
        xp_t = jogador.get("xp_t")
        if not gold_t:
            continue

        encontrou_dado = True
        for minuto, gold in enumerate(gold_t):
            xp = xp_t[minuto] if xp_t and minuto < len(xp_t) else None
            cursor.execute(
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

conexao.commit()
conexao.close()

print(f"{total_inseridos} registros inseridos em 'economia_por_minuto'.")
print(f"{partidas_sem_dado} partidas sem dado de gold_t para jogadores da LGD.")
