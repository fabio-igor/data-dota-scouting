import json
import os
import sqlite3

conexao = sqlite3.connect("data/processed/lgd_scouting.db")
cursor = conexao.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS picks_bans (
        match_id INTEGER,
        ordem INTEGER,
        hero_id INTEGER,
        is_pick BOOLEAN,
        time_lgd BOOLEAN,
        PRIMARY KEY (match_id, ordem)
    )
""")

# Monta um dicionário match_id -> lgd_radiant, consultando a tabela que já temos
cursor.execute("SELECT match_id, lgd_radiant FROM partidas")
mapa_lado_lgd = {
    match_id: bool(lgd_radiant) for match_id, lgd_radiant in cursor.fetchall()
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

    if not picks_bans:
        partidas_sem_draft += 1
        continue

    # Busca o lado da LGD nessa partida a partir do dicionário, não do arquivo JSON
    lgd_radiant = mapa_lado_lgd.get(match_id)

    for evento in picks_bans:
        evento_radiant = evento["team"] == 0
        time_lgd = (evento_radiant == lgd_radiant) if lgd_radiant is not None else None

        cursor.execute(
            """
            INSERT OR REPLACE INTO picks_bans
            (match_id, ordem, hero_id, is_pick, time_lgd)
            VALUES (?, ?, ?, ?, ?)
        """,
            (match_id, evento["order"], evento["hero_id"], evento["is_pick"], time_lgd),
        )
        total_inseridos += 1

conexao.commit()
conexao.close()

print(f"{total_inseridos} eventos de draft inseridos.")
print(f"{partidas_sem_draft} partidas sem dado de draft disponível.")
