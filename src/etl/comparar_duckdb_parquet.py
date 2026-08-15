"""
Compara velocidade: query no banco DuckDB nativo vs. lendo direto do Parquet.
"""

import time

import duckdb

query_duckdb = "SELECT minuto, AVG(gold) FROM economia_por_minuto GROUP BY minuto"
query_parquet = "SELECT minuto, AVG(gold) FROM 'data/processed/parquet/economia_por_minuto.parquet' GROUP BY minuto"

# DuckDB nativo
con = duckdb.connect("data/processed/scouting_platform.duckdb")
t0 = time.perf_counter()
for _ in range(5):
    con.execute(query_duckdb).fetchall()
t_duckdb = (time.perf_counter() - t0) / 5
con.close()

# Parquet direto (sem banco nenhum aberto, só o arquivo)
con2 = duckdb.connect(":memory:")
t0 = time.perf_counter()
for _ in range(5):
    con2.execute(query_parquet).fetchall()
t_parquet = (time.perf_counter() - t0) / 5
con2.close()

print(f"DuckDB nativo : {t_duckdb * 1000:.1f} ms por execução (média de 5)")
print(f"Parquet direto: {t_parquet * 1000:.1f} ms por execução (média de 5)")
