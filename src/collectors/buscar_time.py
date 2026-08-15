"""
Busca o team_id de um time pelo nome, usando o endpoint de busca da OpenDota.
Uso: python src/collectors/buscar_time.py "GamerLegion"
"""
import sys

import requests

if len(sys.argv) < 2:
    print('Uso: python src/collectors/buscar_time.py "Nome do Time"')
    sys.exit(1)

nome_busca = sys.argv[1]
url = f"https://api.opendota.com/api/search?q={nome_busca}"
resposta = requests.get(url)

if resposta.status_code != 200:
    print(f"Erro na busca (status {resposta.status_code})")
    sys.exit(1)

# O endpoint /search retorna jogadores, não times. Pra time, usamos /teams
# (lista completa) e filtramos localmente pelo nome — a API não tem busca
# de time por texto, então trazemos tudo e comparamos.
resposta_times = requests.get("https://api.opendota.com/api/teams")
times = resposta_times.json()

encontrados = [
    t for t in times
    if nome_busca.lower() in (t.get("name") or "").lower()
    or nome_busca.lower() in (t.get("tag") or "").lower()
]

if not encontrados:
    print(f"Nenhum time encontrado com '{nome_busca}' no nome ou tag.")
else:
    print(f"Times encontrados pra '{nome_busca}':\n")
    for t in encontrados[:10]:
        print(f"  team_id={t['team_id']}  nome='{t.get('name')}'  tag='{t.get('tag')}'  rating={t.get('rating', 0):.0f}")
