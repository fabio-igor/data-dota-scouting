import json
import os
import time

import requests

team_id = 10150538
arquivo_lista = "data/raw/lgd_team_matches.json"
pasta_detalhes = "data/raw/match_details"

# Garante que a pasta de detalhes existe
os.makedirs(pasta_detalhes, exist_ok=True)

# Carrega a lista de partidas que já coletamos antes
with open(arquivo_lista, "r", encoding="utf-8") as arquivo:
    partidas = json.load(arquivo)

total = len(partidas)

for i, partida in enumerate(partidas, start=1):
    match_id = partida["match_id"]
    caminho_detalhe = f"{pasta_detalhes}/{match_id}.json"

    # Se esse match_id já foi coletado antes, pula (checkpoint em ação)
    if os.path.exists(caminho_detalhe):
        print(f"[{i}/{total}] Match {match_id} já existe, pulando.")
        continue

    url = f"https://api.opendota.com/api/matches/{match_id}"
    resposta = requests.get(url)

    if resposta.status_code == 200:
        detalhes = resposta.json()
        with open(caminho_detalhe, "w", encoding="utf-8") as arquivo_saida:
            json.dump(detalhes, arquivo_saida, indent=2)
        print(f"[{i}/{total}] Match {match_id} salvo com sucesso.")
    else:
        print(
            f"[{i}/{total}] Erro ao buscar match {match_id} (status {resposta.status_code})"
        )

    time.sleep(1)
