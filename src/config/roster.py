"""
Roster centralizado da LGD Gaming, com período de validade por jogador.

Por que isso existe: antes, o account_id de cada jogador estava hardcoded
em 11 arquivos diferentes (ETL, análises, dashboard). Trocar um jogador do
time significava editar todos manualmente — fácil de esquecer um e gerar
inconsistência. Além disso, um set fixo de IDs não sabe diferenciar
"jogador que já saiu, mas cujas partidas antigas continuam sendo histórico
válido da LGD" de "jogador atual".

data_entrada / data_saida: formato "AAAA-MM-DD", ou None quando não sabemos
a data exata de entrada (jogadores que já estavam no roster antes deste
projeto começar a rastrear) ou quando o jogador ainda está ativo (data_saida
= None significa "sem saída registrada").
"""

from datetime import datetime, timezone

ROSTER = [
    {"account_id": 177203952, "nome": "Yuma", "data_entrada": None, "data_saida": None},
    {"account_id": 292921272, "nome": "Wisper", "data_entrada": None, "data_saida": None},
    {"account_id": 1026694469, "nome": "TaiLung", "data_entrada": None, "data_saida": "2026-08-09"},
    {"account_id": 105045291, "nome": "Thiolicor", "data_entrada": None, "data_saida": None},
    {"account_id": 81306398, "nome": "KJ", "data_entrada": None, "data_saida": None},
    # Stand-in emergencial pro TI 2026, entrou após o banimento do TaiLung.
    # Ainda não está confirmado se é permanente além do TI 2026 — revisar depois do torneio.
    {"account_id": 94054712, "nome": "Topson", "data_entrada": "2026-08-10", "data_saida": None},
]


def _para_data(valor):
    if valor is None:
        return None
    return datetime.strptime(valor, "%Y-%m-%d").replace(tzinfo=timezone.utc)


def jogadores_ativos_em(start_time_unix):
    """
    Retorna o set de account_ids que estavam no roster da LGD na data de
    uma partida (start_time em unix timestamp, como vem da API OpenDota).
    """
    momento = datetime.fromtimestamp(start_time_unix, tz=timezone.utc)
    ativos = set()
    for jogador in ROSTER:
        entrada = _para_data(jogador["data_entrada"])
        saida = _para_data(jogador["data_saida"])
        if entrada and momento < entrada:
            continue
        if saida and momento > saida:
            continue
        ativos.add(jogador["account_id"])
    return ativos


def todos_ids_historicos():
    """
    Todos os account_ids que já passaram pelo roster, sem filtro de data.
    Útil pra ETL que precisa reconhecer partidas antigas (ex: TaiLung) como
    histórico válido da LGD, mesmo que o jogador não esteja mais ativo.
    """
    return {jogador["account_id"] for jogador in ROSTER}


def nome_por_id(account_id):
    for jogador in ROSTER:
        if jogador["account_id"] == account_id:
            return jogador["nome"]
    return None


def nomes_ativos():
    """Nomes dos jogadores sem data_saida — o roster 'atual'."""
    return {j["nome"]: j["account_id"] for j in ROSTER if j["data_saida"] is None}
