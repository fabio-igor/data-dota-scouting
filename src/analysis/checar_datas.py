import sqlite3
from datetime import datetime

conexao = sqlite3.connect("data/processed/lgd_scouting.db")
cursor = conexao.cursor()

cursor.execute("""
    SELECT match_id, start_time, league_name, opposing_team_name
    FROM partidas
    ORDER BY start_time ASC
    LIMIT 5
""")

print("As 5 partidas mais antigas do dataset:\n")
for match_id, start_time, league_name, opponent in cursor.fetchall():
    data = datetime.fromtimestamp(start_time).strftime("%Y-%m-%d")
    print(f"{match_id} | {data} | {league_name} | vs {opponent}")

conexao.close()
