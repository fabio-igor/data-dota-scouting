"""
Coleta as partidas de QUALQUER time (não mais só a LGD).
Uso: python src/collectors/coletar_time.py 10150538

Substitui o fluxo antigo de 2 scripts (um pra lista de partidas, outro pra
detalhes) por um só. A lista de partidas de cada time fica salva separada
(data/raw/times/{team_id}_matches.json), mas os detalhes de cada partida
(data/raw/match_details/) são compartilhados entre todos os times — se dois
times que você rastreia jogaram entre si, a partida só é baixada uma vez.
"""
import json
import os
import sys
import time

import requests

if len(sys.argv) < 2:
    print("Uso: python src/collectors/coletar_time.py <team_id>")
    print('Não sabe o team_id? Roda antes: python src/collectors/buscar_time.py "Nome do Time"')
    sys.exit(1)

team_id = int(sys.argv[1])

pasta_listas = "data/raw/times"
pasta_detalhes = "data/raw/match_details"
os.makedirs(pasta_listas, exist_ok=True)
os.makedirs(pasta_detalhes, exist_ok=True)

# --- Passo 1: lista de partidas do time ---
print(f"Buscando lista de partidas do time {team_id}...")
resposta = requests.get(f"https://api.opendota.com/api/teams/{team_id}/matches")

if resposta.status_code != 200:
    print(f"Erro ao buscar partidas do time (status {resposta.status_code})")
    sys.exit(1)

partidas = resposta.json()
arquivo_lista = f"{pasta_listas}/{team_id}_matches.json"
with open(arquivo_lista, "w", encoding="utf-8") as arquivo:
    json.dump(partidas, arquivo, indent=2)

print(f"{len(partidas)} partidas encontradas, salvas em {arquivo_lista}")

# --- Passo 2: detalhes de cada partida (checkpoint: pula o que já existe) ---
total = len(partidas)
novos = 0

for i, partida in enumerate(partidas, start=1):
    match_id = partida["match_id"]
    caminho_detalhe = f"{pasta_detalhes}/{match_id}.json"

    if os.path.exists(caminho_detalhe):
        continue

    url = f"https://api.opendota.com/api/matches/{match_id}"
    resposta = requests.get(url)

    if resposta.status_code == 200:
        detalhes = resposta.json()
        with open(caminho_detalhe, "w", encoding="utf-8") as arquivo_saida:
            json.dump(detalhes, arquivo_saida, indent=2)
        novos += 1
        print(f"[{i}/{total}] Match {match_id} salvo.")
    else:
        print(f"[{i}/{total}] Erro ao buscar match {match_id} (status {resposta.status_code})")

    time.sleep(1)

print(f"\nConcluído: {novos} partidas novas baixadas ({total - novos} já existiam).")
