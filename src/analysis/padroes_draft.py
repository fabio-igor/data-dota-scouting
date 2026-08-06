import sqlite3

conexao = sqlite3.connect("data/processed/lgd_scouting.db")
cursor = conexao.cursor()

print("=== Top 10 heróis mais PICKADOS pela LGD ===\n")
cursor.execute("""
    SELECT herois.nome_localizado, COUNT(*) as vezes
    FROM picks_bans
    JOIN herois ON picks_bans.hero_id = herois.hero_id
    WHERE picks_bans.time_lgd = 1 AND picks_bans.is_pick = 1
    GROUP BY herois.nome_localizado
    ORDER BY vezes DESC
    LIMIT 10
""")
for heroi, vezes in cursor.fetchall():
    print(f"  {heroi}: {vezes}x")

print("\n=== Top 10 heróis mais BANIDOS pela LGD (contra adversários) ===\n")
cursor.execute("""
    SELECT herois.nome_localizado, COUNT(*) as vezes
    FROM picks_bans
    JOIN herois ON picks_bans.hero_id = herois.hero_id
    WHERE picks_bans.time_lgd = 1 AND picks_bans.is_pick = 0
    GROUP BY herois.nome_localizado
    ORDER BY vezes DESC
    LIMIT 10
""")
for heroi, vezes in cursor.fetchall():
    print(f"  {heroi}: {vezes}x")

print("\n=== Top 10 heróis mais BANIDOS CONTRA a LGD (pelos adversários) ===\n")
cursor.execute("""
    SELECT herois.nome_localizado, COUNT(*) as vezes
    FROM picks_bans
    JOIN herois ON picks_bans.hero_id = herois.hero_id
    WHERE picks_bans.time_lgd = 0 AND picks_bans.is_pick = 0
    GROUP BY herois.nome_localizado
    ORDER BY vezes DESC
    LIMIT 10
""")
for heroi, vezes in cursor.fetchall():
    print(f"  {heroi}: {vezes}x")

conexao.close()
