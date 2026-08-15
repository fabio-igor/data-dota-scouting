"""
Corrigido: inserção em lote (via DataFrame) em vez de uma linha por vez.
Com o volume pequeno (62 partidas), inserir linha por linha não doía.
Com 4000+ partidas, virou um gargalo real — mais de 1 milhão de INSERTs
individuais. Solução: monta tudo em memória primeiro (lista de tuplas),
depois insere de uma vez via pandas DataFrame + DuckDB.
"""

import json
import os

import duckdb
import pandas as pd

conexao = duckdb.connect("data/processed/scouting_platform.duckdb")

conexao.execute("DROP TABLE IF EXISTS economia_por_minuto")

pasta_detalhes = "data/raw/match_details"
linhas = []
partidas_sem_dado = 0

for nome_arquivo in os.listdir(pasta_detalhes):
    caminho = os.path.join(pasta_detalhes, nome_arquivo)

    with open(caminho, "r", encoding="utf-8") as arquivo:
        detalhes = json.load(arquivo)

    match_id = detalhes["match_id"]
    encontrou_dado = False

    for jogador in detalhes["players"]:
        account_id = jogador.get("account_id")
        if account_id is None:
            continue

        gold_t = jogador.get("gold_t")
        xp_t = jogador.get("xp_t")
        if not gold_t:
            continue

        encontrou_dado = True
        for minuto, gold in enumerate(gold_t):
            xp = xp_t[minuto] if xp_t and minuto < len(xp_t) else None
            linhas.append((match_id, account_id, minuto, gold, xp))

    if not encontrou_dado:
        partidas_sem_dado += 1

print(f"{len(linhas)} linhas montadas em memória, inserindo em lote...")

df = pd.DataFrame(linhas, columns=["match_id", "account_id", "minuto", "gold", "xp"])
# Remove duplicatas antes de criar a chave primária (pode acontecer se o
# mesmo match_id/account_id apareceu em mais de uma lista de time)
df = df.drop_duplicates(subset=["match_id", "account_id", "minuto"])

conexao.execute("""
    CREATE TABLE economia_por_minuto AS
    SELECT * FROM df
""")
conexao.execute(
    "ALTER TABLE economia_por_minuto ADD PRIMARY KEY (match_id, account_id, minuto)"
)

conexao.close()

print(f"{len(df)} registros inseridos em 'economia_por_minuto'.")
print(f"{partidas_sem_dado} partidas sem dado de gold_t.")
