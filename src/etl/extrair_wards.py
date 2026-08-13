"""
Recria 'wards_por_jogador'. Esse script não existia no projeto original
(a tabela tinha sido populada uma vez, manualmente, sem o script sobrar) —
reconstruído aqui a partir do campo obs_placed do match_details.
"""
import json
import os

import duckdb

conexao = duckdb.connect("data/processed/scouting_platform.duckdb")

conexao.execute("DROP TABLE IF EXISTS wards_por_jogador")
conexao.execute("""
    CREATE TABLE wards_por_jogador (
        match_id BIGINT,
        account_id BIGINT,
        total_obs_wards INTEGER,
        PRIMARY KEY (match_id, account_id)
    )
""")

pasta_detalhes = "data/raw/match_details"
total_inseridos = 0

for nome_arquivo in os.listdir(pasta_detalhes):
    caminho = os.path.join(pasta_detalhes, nome_arquivo)
    with open(caminho, "r", encoding="utf-8") as arquivo:
        detalhes = json.load(arquivo)

    match_id = detalhes["match_id"]

    for jogador in detalhes["players"]:
        account_id = jogador.get("account_id")
        if account_id is None:
            continue

        conexao.execute(
            """
            INSERT OR REPLACE INTO wards_por_jogador (match_id, account_id, total_obs_wards)
            VALUES (?, ?, ?)
        """,
            (match_id, account_id, jogador.get("obs_placed", 0)),
        )
        total_inseridos += 1

conexao.close()
print(f"{total_inseridos} registros inseridos em 'wards_por_jogador'.")
