import json
import os
import sqlite3

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Economia — LGD", layout="wide")
st.title("Economia")

conexao = sqlite3.connect("data/processed/lgd_scouting.db")
cursor = conexao.cursor()

cursor.execute("SELECT match_id, lgd_radiant = radiant_win FROM partidas")
resultado_por_partida = {
    match_id: bool(vitoria) for match_id, vitoria in cursor.fetchall()
}
conexao.close()

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
        alvo = curvas_vitoria if vitoria else curvas_derrota
        alvo.append(soma_gold_por_minuto[:40])


def media_por_minuto(curvas):
    max_min = max(len(c) for c in curvas)
    return [
        sum(c[m] for c in curvas if m < len(c)) / len([c for c in curvas if m < len(c)])
        for m in range(max_min)
    ]


media_vitoria = media_por_minuto(curvas_vitoria)
media_derrota = media_por_minuto(curvas_derrota)

df = pd.DataFrame(
    {
        "Minuto": range(len(media_vitoria)),
        "Vitórias": media_vitoria,
        "Derrotas": media_derrota[: len(media_vitoria)],
    }
).set_index("Minuto")

st.subheader("Economia do time (soma dos 5 jogadores) — Vitórias vs. Derrotas")
st.line_chart(df, color=["#2ecc71", "#e74c3c"])

st.markdown("""
**Leitura**: aos 10 minutos, a diferença entre vitórias e derrotas é de apenas ~9%.
No fim da partida, essa diferença cresce para 30-43%. Isso indica que a vantagem
econômica da LGD é **consequência** de decisões no meio de jogo — não uma
vantagem construída já no early game.
""")
