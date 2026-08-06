import json
import sqlite3

# Conecta (cria o arquivo .db se não existir ainda)
conexao = sqlite3.connect("data/processed/lgd_scouting.db")
cursor = conexao.cursor()

# Cria a tabela, se ainda não existir
cursor.execute("""
    CREATE TABLE IF NOT EXISTS partidas (
        match_id INTEGER PRIMARY KEY,
        radiant_win BOOLEAN,
        lgd_radiant BOOLEAN,
        lgd_score INTEGER,
        adversario_score INTEGER,
        duration INTEGER,
        start_time INTEGER,
        league_name TEXT,
        opposing_team_name TEXT
    )
""")

# Carrega os dados brutos que já coletamos
with open("data/raw/lgd_team_matches.json", "r", encoding="utf-8") as arquivo:
    partidas = json.load(arquivo)

# Insere cada partida na tabela
for p in partidas:
    lgd_venceu = p["radiant_win"] == p["radiant"]  # se LGD estava no lado que venceu
    lgd_score = p["radiant_score"] if p["radiant"] else p["dire_score"]
    adversario_score = p["dire_score"] if p["radiant"] else p["radiant_score"]

    cursor.execute(
        """
        INSERT OR REPLACE INTO partidas
        (match_id, radiant_win, lgd_radiant, lgd_score, adversario_score,
         duration, start_time, league_name, opposing_team_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            p["match_id"],
            p["radiant_win"],
            p["radiant"],
            lgd_score,
            adversario_score,
            p["duration"],
            p["start_time"],
            p.get("league_name"),
            p.get("opposing_team_name"),
        ),
    )

conexao.commit()
conexao.close()

print(f"{len(partidas)} partidas inseridas na tabela 'partidas'.")
