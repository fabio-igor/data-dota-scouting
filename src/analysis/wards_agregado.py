"""
Wards por jogador, filtrado pra um time (LGD por padrão). Filtra via
jogadores_partida.time_id em vez de uma lista fixa de roster — assim
funciona pra qualquer time que a gente for coletando, só trocando o
LGD_TEAM_ID abaixo por outro (ou parametrizando depois via argumento).
"""
import duckdb

LGD_TEAM_ID = 10150538

conexao = duckdb.connect("data/processed/scouting_platform.duckdb")

resultado = conexao.execute("""
    SELECT jp.account_id,
           AVG(w.total_obs_wards) as media_wards,
           SUM(w.total_obs_wards) as total_wards
    FROM wards_por_jogador w
    JOIN jogadores_partida jp ON w.match_id = jp.match_id AND w.account_id = jp.account_id
    WHERE jp.time_id = ?
    GROUP BY jp.account_id
    ORDER BY media_wards DESC
""", [LGD_TEAM_ID]).fetchall()

print("Wards observadoras por jogador (LGD), média nas partidas:\n")
for account_id, media, total in resultado:
    print(f"  account_id {account_id}: {media:.1f} wards/partida em média ({total} no total)")

conexao.close()
