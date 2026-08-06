import sqlite3

conexao = sqlite3.connect("data/processed/lgd_scouting.db")
cursor = conexao.cursor()

cursor.execute("""
    SELECT partidas.lgd_radiant = partidas.radiant_win as vitoria,
           AVG(jogadores_partida.gpm) as gpm_medio,
           AVG(jogadores_partida.xpm) as xpm_medio,
           AVG(jogadores_partida.kills) as kills_medio,
           AVG(jogadores_partida.deaths) as deaths_medio,
           AVG(jogadores_partida.assists) as assists_medio
    FROM jogadores_partida
    JOIN partidas ON jogadores_partida.match_id = partidas.match_id
    GROUP BY vitoria
""")

print("Métricas médias por jogador da LGD, separadas por resultado da partida:\n")
for vitoria, gpm, xpm, kills, deaths, assists in cursor.fetchall():
    resultado = "Vitórias" if vitoria else "Derrotas"
    print(f"=== {resultado} ===")
    print(f"  GPM médio: {gpm:.0f}")
    print(f"  XPM médio: {xpm:.0f}")
    print(f"  KDA médio: {kills:.1f}/{deaths:.1f}/{assists:.1f}")
    print()

conexao.close()
