import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.config.roster import todos_ids_historicos


with open("data/raw/match_details/8927232410.json", "r", encoding="utf-8") as arquivo:
    detalhes = json.load(arquivo)

jogadores_lgd = todos_ids_historicos()  # importado de src/config/roster.py
nomes = {
    177203952: "Yuma",
    292921272: "Wisper",
    1026694469: "TaiLung",
    105045291: "Thiolicor",
    81306398: "KJ",
}

for jogador in detalhes["players"]:
    account_id = jogador.get("account_id")
    if account_id in jogadores_lgd:
        obs = len(jogador.get("obs_log", []))
        print(f"{nomes[account_id]}: {obs} observer wards")

# Também vamos filtrar objectives por tipo, pra achar eventos de Roshan
print("\nTipos de evento em 'objectives' nessa partida:")
tipos = set(e["type"] for e in detalhes["objectives"])
for tipo in tipos:
    print(f"  {tipo}")
