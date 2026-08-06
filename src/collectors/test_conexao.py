import requests

# Player ID do Yuma
account_id = 177203952

url = f"https://api.opendota.com/api/players/{account_id}"
resposta = requests.get(url)

print("Status code:", resposta.status_code)

if resposta.status_code == 200:
    dados = resposta.json()
    print("Nome do jogador:", dados["profile"]["personaname"])
else:
    print("Algo deu errado ao buscar os dados.")