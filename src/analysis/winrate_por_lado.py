import sqlite3

conexao = sqlite3.connect("data/processed/lgd_scouting.db")
cursor = conexao.cursor()

cursor.execute("""
    SELECT lgd_radiant,
           COUNT(*) as total_partidas,
           SUM(CASE WHEN lgd_radiant = radiant_win THEN 1 ELSE 0 END) as vitorias
    FROM partidas
    GROUP BY lgd_radiant
""")

print("Winrate da LGD por lado:\n")
for lgd_radiant, total, vitorias in cursor.fetchall():
    lado = "Radiant" if lgd_radiant else "Dire"
    winrate = (vitorias / total) * 100
    print(f"  {lado}: {total} partidas, {vitorias} vitórias ({winrate:.1f}% winrate)")

conexao.close()
