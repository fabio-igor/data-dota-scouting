import json

with open("data/raw/match_details/8927232410.json", "r", encoding="utf-8") as arquivo:
    detalhes = json.load(arquivo)

eventos_roshan = [
    e for e in detalhes["objectives"] if e["type"] == "CHAT_MESSAGE_ROSHAN_KILL"
]
print("Estrutura completa de um evento de Roshan:")
for evento in eventos_roshan:
    print(evento)
