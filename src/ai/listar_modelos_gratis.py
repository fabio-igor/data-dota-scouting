"""
Lista os modelos gratuitos disponíveis no OpenRouter AGORA (a lista muda
com frequência, então é melhor perguntar direto à API do que confiar em
um guia salvo).
"""

import requests

resposta = requests.get("https://openrouter.ai/api/v1/models")
modelos = resposta.json()["data"]

gratis = [
    m
    for m in modelos
    if m["pricing"]["prompt"] == "0" and m["pricing"]["completion"] == "0"
]

print(f"{len(gratis)} modelos gratuitos disponíveis agora:\n")
for m in gratis:
    print(f"  {m['id']}  (contexto: {m['context_length']} tokens)")
