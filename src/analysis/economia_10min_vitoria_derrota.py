import sqlite3

conexao = sqlite3.connect("data/processed/lgd_scouting.db")
cursor = conexao.cursor()

cursor.execute("""
    SELECT partidas.lgd_radiant = partidas.radiant_win as vitoria,
           AVG(economia_10min.gold_aos_10min) as gold_medio_10min,
           AVG(economia_10min.xp_aos_10min) as xp_medio_10min
    FROM economia_10min
    JOIN partidas ON economia_10min.match_id = partidas.match_id
    GROUP BY vitoria
""")

print("Economia aos 10 minutos, separada por resultado final da partida:\n")
for vitoria, gold, xp in cursor.fetchall():
    resultado = "Vitórias" if vitoria else "Derrotas"
    print(f"  {resultado}: {gold:.0f} gold, {xp:.0f} xp (aos 10min)")

conexao.close()
