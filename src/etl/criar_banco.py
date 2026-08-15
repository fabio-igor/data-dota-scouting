"""
Cria/atualiza as tabelas 'times' e 'partidas' no banco multi-time (DuckDB).

Lê TODAS as listas de partidas em data/raw/times/*.json (uma por time
coletado, nomeada {team_id}_matches.json — geradas por coletar_time.py).
Se dois times que você rastreia jogaram entre si, a partida aparece nas
duas listas; o INSERT OR REPLACE (chave = match_id) resolve a duplicata
sem problema, mantendo só uma linha.
"""

import glob
import json
import os

import duckdb

conexao = duckdb.connect("data/processed/scouting_platform.duckdb")

conexao.execute("""
    CREATE TABLE IF NOT EXISTS times (
        time_id BIGINT PRIMARY KEY,
        nome VARCHAR,
        tier VARCHAR,
        regiao VARCHAR
    )
""")

conexao.execute("DROP TABLE IF EXISTS partidas")
conexao.execute("""
    CREATE TABLE partidas (
        match_id BIGINT PRIMARY KEY,
        radiant_team_id BIGINT,
        dire_team_id BIGINT,
        radiant_win BOOLEAN,
        radiant_score INTEGER,
        dire_score INTEGER,
        duration INTEGER,
        start_time BIGINT,
        league_name VARCHAR
    )
""")

adversarios_vistos = {}
total_partidas_processadas = 0

for caminho_lista in glob.glob("data/raw/times/*_matches.json"):
    nome_arquivo = os.path.basename(caminho_lista)
    team_id_coletado = int(nome_arquivo.replace("_matches.json", ""))

    # Se ainda não sabemos o nome desse time coletado, deixa NULL por
    # enquanto — o nome real vem de opposing_team_name quando esse time
    # aparecer como adversário em outra lista. Se nunca aparecer, dá pra
    # completar manualmente.
    conexao.execute(
        "INSERT INTO times VALUES (?, NULL, NULL, NULL) ON CONFLICT DO NOTHING",
        [team_id_coletado],
    )

    with open(caminho_lista, "r", encoding="utf-8") as arquivo:
        partidas = json.load(arquivo)

    for p in partidas:
        eu_radiant = p["radiant"]
        adversario_id = p.get("opposing_team_id")
        adversario_nome = p.get("opposing_team_name")

        if adversario_id and adversario_id not in adversarios_vistos:
            adversarios_vistos[adversario_id] = adversario_nome

        radiant_team_id = team_id_coletado if eu_radiant else adversario_id
        dire_team_id = adversario_id if eu_radiant else team_id_coletado

        conexao.execute(
            """
            INSERT OR REPLACE INTO partidas
            (match_id, radiant_team_id, dire_team_id, radiant_win, radiant_score,
             dire_score, duration, start_time, league_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                p["match_id"],
                radiant_team_id,
                dire_team_id,
                p["radiant_win"],
                p["radiant_score"],
                p["dire_score"],
                p["duration"],
                p["start_time"],
                p.get("league_name"),
            ),
        )
        total_partidas_processadas += 1

# Popula/atualiza 'times' com nome real de cada adversário visto
for adversario_id, nome in adversarios_vistos.items():
    conexao.execute(
        "INSERT INTO times VALUES (?, ?, NULL, NULL) ON CONFLICT (time_id) DO UPDATE SET nome = EXCLUDED.nome",
        [adversario_id, nome],
    )

# Nome da LGD (nosso time principal) — não vem como "adversário" de
# ninguém na própria lista dele, então garantimos aqui.
conexao.execute(
    "INSERT INTO times VALUES (10150538, 'LGD Gaming', '1', 'SA') ON CONFLICT (time_id) DO UPDATE SET nome = 'LGD Gaming'"
)

total_partidas = conexao.execute("SELECT COUNT(*) FROM partidas").fetchone()[0]
total_times = conexao.execute("SELECT COUNT(*) FROM times").fetchone()[0]
conexao.close()

print(f"{total_partidas_processadas} linhas processadas de {len(glob.glob('data/raw/times/*_matches.json'))} lista(s) de time.")
print(f"{total_partidas} partidas únicas na tabela 'partidas'.")
print(f"{total_times} times na tabela 'times'.")
