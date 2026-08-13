"""
Cria/atualiza as tabelas 'times' e 'partidas' no banco multi-time (DuckDB).

Descoberta ao migrar: o JSON que o coletor já baixa (lgd_team_matches.json,
vindo do endpoint /teams/{id}/matches da OpenDota) já traz opposing_team_id
— o ID de verdade do adversário, não só o nome. O ETL antigo ignorava esse
campo. Isso significa que dá pra popular a tabela 'times' com todo mundo
que a LGD já enfrentou, sem nenhuma chamada de API extra.

LGD_TEAM_ID: nosso próprio time. Quando começarmos a coletar o ponto de
vista de outros times (não só partidas onde a LGD jogou), essa constante
vira parâmetro.
"""

import json

import duckdb

LGD_TEAM_ID = 10150538

conexao = duckdb.connect("data/processed/scouting_platform.duckdb")

conexao.execute("""
    CREATE TABLE IF NOT EXISTS times (
        time_id BIGINT PRIMARY KEY,
        nome VARCHAR,
        tier VARCHAR,
        regiao VARCHAR
    )
""")
conexao.execute(
    "INSERT INTO times VALUES (?, 'LGD Gaming', '1', 'SA') ON CONFLICT (time_id) DO UPDATE SET nome = 'LGD Gaming'",
    [LGD_TEAM_ID],
)

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

with open("data/raw/lgd_team_matches.json", "r", encoding="utf-8") as arquivo:
    partidas = json.load(arquivo)

adversarios_vistos = {}

for p in partidas:
    lgd_radiant = p["radiant"]
    adversario_id = p.get("opposing_team_id")
    adversario_nome = p.get("opposing_team_name")

    if adversario_id and adversario_id not in adversarios_vistos:
        adversarios_vistos[adversario_id] = adversario_nome

    radiant_team_id = LGD_TEAM_ID if lgd_radiant else adversario_id
    dire_team_id = adversario_id if lgd_radiant else LGD_TEAM_ID

    conexao.execute(
        """
        INSERT INTO partidas
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

# Popula 'times' com todo adversário que apareceu (tier/regiao ficam
# desconhecidos por enquanto — dá pra completar manualmente ou via API depois)
for adversario_id, nome in adversarios_vistos.items():
    conexao.execute(
        "INSERT INTO times VALUES (?, ?, NULL, NULL) ON CONFLICT (time_id) DO UPDATE SET nome = EXCLUDED.nome",
        [adversario_id, nome],
    )

conexao.close()

print(f"{len(partidas)} partidas inseridas na tabela 'partidas'.")
print(f"{len(adversarios_vistos)} adversários novos inseridos na tabela 'times'.")
