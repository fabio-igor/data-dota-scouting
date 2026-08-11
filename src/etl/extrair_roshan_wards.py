import json
import os
import sqlite3
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.config.roster import todos_ids_historicos


conexao = sqlite3.connect("data/processed/lgd_scouting.db")
cursor = conexao.cursor()

# Recria a tabela incluindo o time responsável
cursor.execute("DROP TABLE IF EXISTS roshan_kills")
cursor.execute("""
    CREATE TABLE roshan_kills (
        match_id INTEGER,
        ordem INTEGER,
        tempo_segundos INTEGER,
        time_lgd BOOLEAN,
        PRIMARY KEY (match_id, ordem)
    )
""")

# Reaproveita o mapa match_id -> lgd_radiant, já usado na Etapa 5
cursor.execute("SELECT match_id, lgd_radiant FROM partidas")
mapa_lado_lgd = {
    match_id: bool(lgd_radiant) for match_id, lgd_radiant in cursor.fetchall()
}

jogadores_lgd = todos_ids_historicos()  # importado de src/config/roster.py
pasta_detalhes = "data/raw/match_details"
total_inseridos = 0

for nome_arquivo in os.listdir(pasta_detalhes):
    caminho = os.path.join(pasta_detalhes, nome_arquivo)
    with open(caminho, "r", encoding="utf-8") as arquivo:
        detalhes = json.load(arquivo)

    match_id = detalhes["match_id"]
    lgd_radiant = mapa_lado_lgd.get(match_id)

    eventos_roshan = [
        e
        for e in detalhes.get("objectives", [])
        if e["type"] == "CHAT_MESSAGE_ROSHAN_KILL"
    ]
    for ordem, evento in enumerate(eventos_roshan):
        # team: 2 = radiant, 3 = dire
        evento_radiant = evento["team"] == 2
        time_lgd = (evento_radiant == lgd_radiant) if lgd_radiant is not None else None

        cursor.execute(
            """
            INSERT OR REPLACE INTO roshan_kills (match_id, ordem, tempo_segundos, time_lgd)
            VALUES (?, ?, ?, ?)
        """,
            (match_id, ordem, evento["time"], time_lgd),
        )
        total_inseridos += 1

conexao.commit()

# Já aproveita pra consultar o resultado agregado
cursor.execute("""
    SELECT time_lgd, COUNT(*) as total, AVG(tempo_segundos) as tempo_medio
    FROM roshan_kills
    GROUP BY time_lgd
""")
print(f"\n{total_inseridos} eventos de Roshan processados.\n")
for time_lgd, total, tempo_medio in cursor.fetchall():
    quem = "LGD" if time_lgd else "Adversário"
    minutos = tempo_medio / 60
    print(f"  {quem}: {total} Roshans, tempo médio {minutos:.1f} min")

conexao.close()
