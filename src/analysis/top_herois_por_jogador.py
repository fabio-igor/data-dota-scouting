import sqlite3

conexao = sqlite3.connect("data/processed/lgd_scouting.db")
cursor = conexao.cursor()

# Nomes dos jogadores, pra exibir de forma legível (não temos isso salvo em tabela ainda)
nomes_jogadores = {
    177203952: "Yuma",
    292921272: "Wisper",
    1026694469: "TaiLung",
    105045291: "Thiolicor",
    81306398: "KJ"
}

for account_id, nome in nomes_jogadores.items():
    cursor.execute("""
        SELECT herois.nome_localizado,
               COUNT(*) as partidas_jogadas,
               SUM(CASE WHEN partidas.lgd_radiant = partidas.radiant_win THEN 1 ELSE 0 END) as vitorias
        FROM jogadores_partida
        JOIN herois ON jogadores_partida.hero_id = herois.hero_id
        JOIN partidas ON jogadores_partida.match_id = partidas.match_id
        WHERE jogadores_partida.account_id = ?
        GROUP BY herois.nome_localizado
        HAVING partidas_jogadas >= 2
        ORDER BY partidas_jogadas DESC, vitorias DESC
        LIMIT 5
    """, (account_id,))

    resultados = cursor.fetchall()

    print(f"\n=== Top heróis de {nome} ===")
    for heroi, jogadas, vitorias in resultados:
        winrate = (vitorias / jogadas) * 100
        print(f"  {heroi}: {jogadas} partidas, {vitorias} vitórias ({winrate:.0f}% winrate)")

conexao.close()