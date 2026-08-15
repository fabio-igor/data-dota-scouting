import sqlite3

import duckdb
import pandas as pd

CAMINHO_SQLITE = "data/processed/lgd_scouting.db"
CAMINHO_DUCKDB = "data/processed/lgd_scouting.duckdb"

con_sqlite = sqlite3.connect(CAMINHO_SQLITE)
tabelas = [
    row[0]
    for row in con_sqlite.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
]

con_duck = duckdb.connect(CAMINHO_DUCKDB)

for tabela in tabelas:
    df = pd.read_sql_query(f"SELECT * FROM {tabela}", con_sqlite)
    # DuckDB cria a tabela direto a partir do DataFrame, inferindo os tipos
    con_duck.execute(f"CREATE OR REPLACE TABLE {tabela} AS SELECT * FROM df")
    n_sqlite = len(df)
    n_duck = con_duck.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
    status = "OK" if n_sqlite == n_duck else "DIVERGÊNCIA"
    print(f"{tabela}: {n_sqlite} linhas (SQLite) -> {n_duck} linhas (DuckDB) [{status}]")

con_sqlite.close()
con_duck.close()

print(f"\nMigração concluída. Arquivo DuckDB salvo em: {CAMINHO_DUCKDB}")
