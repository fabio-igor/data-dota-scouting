import json
import os
import sqlite3
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.config.roster import todos_ids_historicos

conexao = sqlite3.connect("data/processed/lgd_scouting.db")
cursor = conexao.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS jogadores_partida (
        match_id INTEGER,
        account_id INTEGER,
        hero_id INTEGER,
        kills INTEGER,
        deaths INTEGER,
        assists INTEGER,
        gpm INTEGER,
        xpm INTEGER,
        PRIMARY KEY (match_id, account_id)
    )
""")

# IDs de todos que já passaram pelo roster da LGD (histórico completo),
# vindos de src/config/roster.py — não mais hardcoded aqui.
jogadores_lgd = todos_ids_historicos()

pasta_detalhes = "data/raw/match_details"
total_inseridos = 0

for nome_arquivo in os.listdir(pasta_detalhes):
    caminho = os.path.join(pasta_detalhes, nome_arquivo)

    with open(caminho, "r", encoding="utf-8") as arquivo:
        detalhes = json.load(arquivo)

    match_id = detalhes["match_id"]

    for jogador in detalhes["players"]:
        account_id = jogador.get("account_id")

        # Só nos interessam os 5 jogadores da LGD, não os adversários
        if account_id not in jogadores_lgd:
            continue

        cursor.execute(
            """
            INSERT OR REPLACE INTO jogadores_partida
            (match_id, account_id, hero_id, kills, deaths, assists, gpm, xpm)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                match_id,
                account_id,
                jogador["hero_id"],
                jogador["kills"],
                jogador["deaths"],
                jogador["assists"],
                jogador["gold_per_min"],
                jogador["xp_per_min"],
            ),
        )
        total_inseridos += 1

conexao.commit()
conexao.close()

print(f"{total_inseridos} registros inseridos em 'jogadores_partida'.")
