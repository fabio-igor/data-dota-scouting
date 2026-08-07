import sqlite3

conexao = sqlite3.connect("data/processed/lgd_scouting.db")
cursor = conexao.cursor()

nomes = {
    177203952: "Yuma",
    292921272: "Wisper",
    1026694469: "TaiLung",
    105045291: "Thiolicor",
    81306398: "KJ",
}

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
