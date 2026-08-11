import os
import sqlite3
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.config.roster import ROSTER

conexao = sqlite3.connect("data/processed/lgd_scouting.db")
cursor = conexao.cursor()

nomes = {j["account_id"]: j["nome"] for j in ROSTER}

cursor.execute("""
    SELECT account_id, AVG(total_obs_wards) as media_wards, SUM(total_obs_wards) as total_wards
    FROM wards_por_jogador
    GROUP BY account_id
    ORDER BY media_wards DESC
""")

print("Wards observadoras por jogador, média nas 62 partidas:\n")
for account_id, media, total in cursor.fetchall():
    print(
        f"  {nomes[account_id]}: {media:.1f} wards/partida em média ({total} no total)"
    )

conexao.close()
