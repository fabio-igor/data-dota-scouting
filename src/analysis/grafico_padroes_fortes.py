import sqlite3

import matplotlib.pyplot as plt

conexao = sqlite3.connect("data/processed/lgd_scouting.db")
cursor = conexao.cursor()

# Heróis e jogadores dos padrões classificados como "fortes" na Etapa 10
destaques = [
    ("Hoodwink", 105045291, "Thiolicor"),
    ("Bane", 81306398, "KJ"),
    ("Huskar", 1026694469, "TaiLung"),
]

labels = []
winrates = []
partidas_contagem = []

for hero_nome, account_id, jogador_nome in destaques:
    cursor.execute(
        """
        SELECT COUNT(*),
               SUM(CASE WHEN partidas.lgd_radiant = partidas.radiant_win THEN 1 ELSE 0 END)
        FROM jogadores_partida
        JOIN herois ON jogadores_partida.hero_id = herois.hero_id
        JOIN partidas ON jogadores_partida.match_id = partidas.match_id
        WHERE jogadores_partida.account_id = ? AND herois.nome_localizado = ?
    """,
        (account_id, hero_nome),
    )

    total, vitorias = cursor.fetchone()
    winrate = (vitorias / total) * 100

    labels.append(f"{jogador_nome}\n{hero_nome}")
    winrates.append(winrate)
    partidas_contagem.append(total)

conexao.close()

plt.figure(figsize=(8, 6))
barras = plt.bar(labels, winrates, color="darkgreen")
plt.ylabel("Winrate (%)")
plt.title("Padrões fortes identificados: winrate por combinação jogador-herói")
plt.axhline(50, color="gray", linestyle="--", alpha=0.5, label="50% (referência)")

# Anota cada barra com o número de partidas, pra não esconder o tamanho da amostra
for barra, n in zip(barras, partidas_contagem):
    plt.text(
        barra.get_x() + barra.get_width() / 2,
        barra.get_height() + 2,
        f"n={n}",
        ha="center",
    )

plt.legend()
plt.tight_layout()
plt.savefig("reports/padroes_fortes_winrate.png", dpi=150)
print("Gráfico salvo em reports/padroes_fortes_winrate.png")
