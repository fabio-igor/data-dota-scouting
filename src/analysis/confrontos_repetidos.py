import sqlite3

conexao = sqlite3.connect("data/processed/lgd_scouting.db")
cursor = conexao.cursor()

cursor.execute("""
    SELECT opposing_team_name, COUNT(*) as vezes
    FROM partidas
    GROUP BY opposing_team_name
    ORDER BY vezes DESC
""")

print("Quantas vezes a LGD enfrentou cada adversário:\n")
for time, vezes in cursor.fetchall():
    print(f"  {time}: {vezes}x")

conexao.close()
