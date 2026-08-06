import sqlite3

conexao = sqlite3.connect("data/processed/lgd_scouting.db")
cursor = conexao.cursor()

adversarios_relevantes = ["Team Yandex", "BoomBoys", "PlayTime"]

for adversario in adversarios_relevantes:
    cursor.execute(
        """
        SELECT herois.nome_localizado, COUNT(*) as vezes
        FROM picks_bans
        JOIN herois ON picks_bans.hero_id = herois.hero_id
        JOIN partidas ON picks_bans.match_id = partidas.match_id
        WHERE picks_bans.time_lgd = 1
          AND picks_bans.is_pick = 0
          AND partidas.opposing_team_name = ?
        GROUP BY herois.nome_localizado
        ORDER BY vezes DESC
        LIMIT 5
    """,
        (adversario,),
    )

    resultados = cursor.fetchall()
    total_confrontos = {"Team Yandex": 10, "BoomBoys": 8, "PlayTime": 6}[adversario]

    print(f"\n=== Bans da LGD contra {adversario} ({total_confrontos} confrontos) ===")
    for heroi, vezes in resultados:
        print(
            f"  {heroi}: {vezes}x ({vezes / total_confrontos * 100:.0f}% dos confrontos)"
        )

conexao.close()
