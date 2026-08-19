import json
import os

import duckdb

conexao = duckdb.connect("data/processed/scouting_platform.duckdb")

conexao.execute("DROP TABLE IF EXISTS jogadores_partida")
conexao.execute("""
    CREATE TABLE jogadores_partida (
        match_id BIGINT,
        account_id BIGINT,
        time_id BIGINT,
        hero_id INTEGER,
        kills INTEGER,
        deaths INTEGER,
        assists INTEGER,
        gpm INTEGER,
        xpm INTEGER,
        PRIMARY KEY (match_id, account_id)
    )
""")

conexao.execute("""
    CREATE TABLE IF NOT EXISTS jogadores (
        account_id BIGINT PRIMARY KEY,
        nome VARCHAR,
        time_id_atual BIGINT
    )
""")

# time_id + start_time de cada partida — o start_time serve pra saber qual
# é o registro MAIS RECENTE de nome/time de cada jogador (nomes de pro
# player raramente mudam, mas o time pode; ficamos com o mais novo visto).
info_partidas = {
    row[0]: (row[1], row[2], row[3])
    for row in conexao.execute(
        "SELECT match_id, radiant_team_id, dire_team_id, start_time FROM partidas"
    ).fetchall()
}

pasta_detalhes = "data/raw/match_details"
arquivos = os.listdir(pasta_detalhes)
total_arquivos = len(arquivos)
total_inseridos = 0

# account_id -> (nome, time_id, start_time_da_partida_mais_recente_visto)
melhor_registro_jogador = {}

for i, nome_arquivo in enumerate(arquivos, start=1):
    if i % 500 == 0 or i == total_arquivos:
        print(f"  processando... {i}/{total_arquivos} arquivos")

    caminho = os.path.join(pasta_detalhes, nome_arquivo)

    with open(caminho, "r", encoding="utf-8") as arquivo:
        detalhes = json.load(arquivo)

    match_id = detalhes["match_id"]
    if match_id not in info_partidas:
        continue
    radiant_team_id, dire_team_id, start_time = info_partidas[match_id]

    for jogador in detalhes["players"]:
        account_id = jogador.get("account_id")
        if account_id is None:
            continue  # perfil privado na Steam, API não devolve o account_id

        time_id = radiant_team_id if jogador["isRadiant"] else dire_team_id

        conexao.execute(
            """
            INSERT OR REPLACE INTO jogadores_partida
            (match_id, account_id, time_id, hero_id, kills, deaths, assists, gpm, xpm)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                match_id,
                account_id,
                time_id,
                jogador["hero_id"],
                jogador["kills"],
                jogador["deaths"],
                jogador["assists"],
                jogador["gold_per_min"],
                jogador["xp_per_min"],
            ),
        )
        total_inseridos += 1

        nome = jogador.get("name")
        if nome:
            registro_atual = melhor_registro_jogador.get(account_id)
            if registro_atual is None or start_time > registro_atual[2]:
                melhor_registro_jogador[account_id] = (nome, time_id, start_time)

print(
    f"\nAtualizando tabela 'jogadores' com {len(melhor_registro_jogador)} jogadores..."
)
for account_id, (nome, time_id, _) in melhor_registro_jogador.items():
    conexao.execute(
        """
        INSERT INTO jogadores (account_id, nome, time_id_atual) VALUES (?, ?, ?)
        ON CONFLICT (account_id) DO UPDATE SET nome = EXCLUDED.nome, time_id_atual = EXCLUDED.time_id_atual
    """,
        (account_id, nome, time_id),
    )

conexao.close()

print(f"\n{total_inseridos} registros inseridos em 'jogadores_partida'.")
print(f"{len(melhor_registro_jogador)} jogadores com nome conhecido em 'jogadores'.")
