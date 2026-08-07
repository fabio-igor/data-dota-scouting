import json

with open("data/raw/match_details/8927232410.json", "r", encoding="utf-8") as arquivo:
    detalhes = json.load(arquivo)

jogadores_lgd = {177203952, 292921272, 1026694469, 105045291, 81306398}
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
