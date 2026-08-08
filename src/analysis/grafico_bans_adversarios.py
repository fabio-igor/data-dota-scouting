import matplotlib.pyplot as plt

# Dados já validados na Etapa 10 (bans que se destacam por adversário)
dados = [
    ("Enigma\n(vs Team Yandex)", 50),
    ("Keeper of the Light\n(vs BoomBoys)", 38),
    ("Invoker\n(vs BoomBoys)", 38),
    ("Enchantress\n(vs PlayTime)", 100),
    ("Nyx Assassin\n(vs PlayTime)", 67),
]

labels = [d[0] for d in dados]
valores = [d[1] for d in dados]

plt.figure(figsize=(9, 6))
cores = ["#3498db", "#e67e22", "#e67e22", "#2ecc71", "#2ecc71"]  # cor por adversário
barras = plt.bar(labels, valores, color=cores)

plt.ylabel("% dos confrontos em que foi banido")
plt.title("Bans direcionados por adversário (confrontos com histórico de reencontro)")
plt.ylim(0, 110)

for barra, valor in zip(barras, valores):
    plt.text(barra.get_x() + barra.get_width() / 2, valor + 2, f"{valor}%", ha="center")

plt.xticks(rotation=15, ha="right")
plt.tight_layout()
plt.savefig("reports/bans_por_adversario.png", dpi=150)
print("Gráfico salvo em reports/bans_por_adversario.png")
