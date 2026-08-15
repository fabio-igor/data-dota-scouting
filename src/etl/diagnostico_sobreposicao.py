"""
Diagnóstico: será que alguma partida da LGD também aparece na lista de
outro time coletado (mesmo match_id em 2 arquivos)? Se sim, o
criar_banco.py pode estar processando a mesma partida duas vezes com
dados ligeiramente diferentes, e a segunda sobrescreve a primeira.
"""

import glob
import json
import os

listas = {}
for caminho in glob.glob("data/raw/times/*_matches.json"):
    team_id = os.path.basename(caminho).replace("_matches.json", "")
    with open(caminho, "r", encoding="utf-8") as f:
        partidas = json.load(f)
    listas[team_id] = {p["match_id"] for p in partidas}
    print(f"{team_id}: {len(listas[team_id])} partidas")

print()
lgd_id = "10150538"
if lgd_id not in listas:
    print("Não achei a lista da LGD, confere o nome do arquivo.")
else:
    lgd_matches = listas[lgd_id]
    print(f"LGD tem {len(lgd_matches)} partidas na lista.")
    for outro_id, matches in listas.items():
        if outro_id == lgd_id:
            continue
        sobreposicao = lgd_matches & matches
        if sobreposicao:
            print(
                f"  SOBREPOSIÇÃO com {outro_id}: {len(sobreposicao)} partidas em comum -> {sorted(sobreposicao)[:5]}..."
            )

print()
print(
    "Total de match_id únicos entre TODAS as listas:",
    len(set().union(*listas.values())),
)
print(
    "Soma se não houvesse sobreposição nenhuma:", sum(len(v) for v in listas.values())
)
