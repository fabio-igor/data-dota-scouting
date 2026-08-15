"""
Exporta todas as tabelas do scouting_platform.duckdb para Parquet.

Por que Parquet: formato colunar comprimido (cada coluna fica junta no
disco). Numa tabela como economia_por_minuto (milhões de linhas, poucas
colunas), isso compacta muito e acelera queries que só usam algumas
colunas — não precisa ler o arquivo inteiro pra somar uma coluna.

DuckDB já sabe ler/escrever Parquet nativamente, sem lib extra.
"""

import os

import duckdb

conexao = duckdb.connect("data/processed/scouting_platform.duckdb")

pasta_parquet = "data/processed/parquet"
os.makedirs(pasta_parquet, exist_ok=True)

tabelas = [row[0] for row in conexao.execute("SHOW TABLES").fetchall()]

print(f"{len(tabelas)} tabelas encontradas: {tabelas}\n")

tamanho_duckdb = os.path.getsize("data/processed/scouting_platform.duckdb")
tamanho_parquet_total = 0

for tabela in tabelas:
    caminho_saida = f"{pasta_parquet}/{tabela}.parquet"
    conexao.execute(
        f"COPY {tabela} TO '{caminho_saida}' (FORMAT PARQUET, COMPRESSION ZSTD)"
    )
    tamanho = os.path.getsize(caminho_saida)
    tamanho_parquet_total += tamanho
    n_linhas = conexao.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
    print(f"  {tabela}: {n_linhas} linhas -> {tamanho / 1024:.1f} KB")

conexao.close()

print(f"\nBanco DuckDB original: {tamanho_duckdb / 1024 / 1024:.2f} MB")
print(f"Soma dos arquivos Parquet: {tamanho_parquet_total / 1024 / 1024:.2f} MB")
print(f"Redução: {(1 - tamanho_parquet_total / tamanho_duckdb) * 100:.1f}%")
