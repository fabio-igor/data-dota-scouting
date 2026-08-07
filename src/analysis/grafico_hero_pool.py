import sqlite3

import matplotlib.pyplot as plt

conexao = sqlite3.connect("data/processed/lgd_scouting.db")
cursor = conexao.cursor()

cursor.execute("""
    SELECT herois.nome_localizado, COUNT(*) as vezes
    FROM picks_bans
    JOIN herois ON picks_bans.hero_id = herois.hero_id
    WHERE picks_bans.time_lgd = 1 AND picks_bans.is_pick = 1
    GROUP BY herois.nome_localizado
    ORDER BY vezes DESC
    LIMIT 10
""")

resultados = cursor.fetchall()
conexao.close()

herois = [r[0] for r in resultados]
valores = [r[1] for r in resultados]

# Inverte a ordem pra o herói mais pickado aparecer no topo do gráfico
herois.reverse()
valores.reverse()

plt.figure(figsize=(9, 6))
plt.barh(herois, valores, color="steelblue")
plt.xlabel("Vezes pickado")
plt.title("Top 10 heróis mais pickados pela LGD")
plt.tight_layout()
plt.savefig("reports/hero_pool_time.png", dpi=150)
print("Gráfico salvo em reports/hero_pool_time.png")
