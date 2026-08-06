import sqlite3

import requests

conexao = sqlite3.connect("data/processed/lgd_scouting.db")
cursor = conexao.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS herois (
        hero_id INTEGER PRIMARY KEY,
        nome TEXT,
        nome_localizado TEXT
    )
""")

resposta = requests.get("https://api.opendota.com/api/heroes")

if resposta.status_code == 200:
    herois = resposta.json()

    for h in herois:
        cursor.execute(
            """
            INSERT OR REPLACE INTO herois (hero_id, nome, nome_localizado)
            VALUES (?, ?, ?)
        """,
            (h["id"], h["name"], h["localized_name"]),
        )

    conexao.commit()
    print(f"{len(herois)} heróis inseridos na tabela de referência.")
else:
    print(f"Erro ao buscar heróis (status {resposta.status_code})")

conexao.close()
