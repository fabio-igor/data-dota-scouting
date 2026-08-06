import sqlite3

conexao = sqlite3.connect("data/processed/lgd_scouting.db")
cursor = conexao.cursor()

# Checagem 1: duplicatas em 'partidas' (não deveria haver, já que match_id é chave primária, mas vamos confirmar)
cursor.execute("SELECT COUNT(*), COUNT(DISTINCT match_id) FROM partidas")
total, distintos = cursor.fetchone()
print(f"Partidas: {total} linhas, {distintos} match_id distintos")

# Checagem 2: partidas com duração suspeita (muito curta ou muito longa)
cursor.execute("SELECT match_id, duration FROM partidas WHERE duration < 600 OR duration > 5400")
suspeitas = cursor.fetchall()
print(f"Partidas com duração suspeita (<10min ou >90min): {len(suspeitas)}")
for match_id, duration in suspeitas:
    print(f"  {match_id}: {duration}s")

# Checagem 3: jogadores_partida sem herói registrado
cursor.execute("SELECT COUNT(*) FROM jogadores_partida WHERE hero_id IS NULL OR hero_id = 0")
sem_heroi = cursor.fetchone()[0]
print(f"Registros de jogador sem hero_id válido: {sem_heroi}")

conexao.close()