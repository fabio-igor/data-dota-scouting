import duckdb

con = duckdb.connect("data/processed/scouting_platform.duckdb")
resultado = con.execute(
    "SELECT time_id, nome FROM times WHERE nome ILIKE '%LGD%'"
).fetchall()
print(f"{len(resultado)} time(s) encontrado(s) com 'LGD' no nome:")
for time_id, nome in resultado:
    print(f"  time_id={time_id}  nome='{nome}'")
