import json
import os
import sqlite3

import matplotlib.pyplot as plt

conexao = sqlite3.connect("data/processed/lgd_scouting.db")
cursor = conexao.cursor()

cursor.execute("SELECT match_id, lgd_radiant = radiant_win FROM partidas")
resultado_por_partida = {
    match_id: bool(vitoria) for match_id, vitoria in cursor.fetchall()
}

jogadores_lgd = {177203952, 292921272, 1026694469, 105045291, 81306398}
pasta_detalhes = "data/raw/match_details"

curvas_vitoria = []
curvas_derrota = []

for nome_arquivo in os.listdir(pasta_detalhes):
    caminho = os.path.join(pasta_detalhes, nome_arquivo)
    with open(caminho, "r", encoding="utf-8") as arquivo:
        detalhes = json.load(arquivo)

    match_id = detalhes["match_id"]
    vitoria = resultado_por_partida.get(match_id)

    # Soma o gold_t dos 5 jogadores da LGD, minuto a minuto
    soma_gold_por_minuto = None
    for jogador in detalhes["players"]:
        if jogador.get("account_id") not in jogadores_lgd:
            continue
        gold_t = jogador.get("gold_t")
        if not gold_t:
            continue
        if soma_gold_por_minuto is None:
            soma_gold_por_minuto = gold_t.copy()
        else:
            for i in range(min(len(soma_gold_por_minuto), len(gold_t))):
                soma_gold_por_minuto[i] += gold_t[i]

    if soma_gold_por_minuto:
        if vitoria:
            curvas_vitoria.append(
                soma_gold_por_minuto[:40]
            )  # limita a 40min pra padronizar
        else:
            curvas_derrota.append(soma_gold_por_minuto[:40])

conexao.close()


# Calcula a média minuto a minuto entre as partidas de cada grupo
def media_por_minuto(curvas):
    max_min = max(len(c) for c in curvas)
    medias = []
    for minuto in range(max_min):
        valores = [c[minuto] for c in curvas if minuto < len(c)]
        medias.append(sum(valores) / len(valores))
    return medias


media_vitoria = media_por_minuto(curvas_vitoria)
media_derrota = media_por_minuto(curvas_derrota)

plt.figure(figsize=(10, 6))
plt.plot(media_vitoria, label="Vitórias", color="green")
plt.plot(media_derrota, label="Derrotas", color="red")
plt.xlabel("Minuto de jogo")
plt.ylabel("Gold total do time (soma dos 5 jogadores)")
plt.title("Economia da LGD ao longo do jogo: Vitórias vs. Derrotas")
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig("reports/economia_vitoria_derrota.png", dpi=150)
print("Gráfico salvo em reports/economia_vitoria_derrota.png")
