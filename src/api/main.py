"""
API do scouting. Roda local com:
    uvicorn src.api.main:app --reload

Depois de rodar, abre http://localhost:8000/docs — o FastAPI gera uma
página de teste automática pra cada endpoint, sem precisar escrever nada
a mais pra isso.
"""

import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
import duckdb

from src.ai.perguntar import descrever_schema, formatar_resposta, gerar_sql, rodar_sql

CAMINHO_BANCO = "data/processed/scouting_platform.duckdb"

app = FastAPI(title="Dota Scouting API")

# Libera qualquer origem por enquanto (frontend local vai rodar em outra
# porta). Quando for pra produção de verdade, restringe pro domínio real.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def raiz():
    return {"status": "ok", "mensagem": "API de scouting no ar"}


@app.get("/times")
def listar_times(busca: str = ""):
    """Lista times. Opcionalmente filtra por nome (busca parcial)."""
    conexao = duckdb.connect(CAMINHO_BANCO, read_only=True)
    if busca:
        resultado = conexao.execute(
            "SELECT time_id, nome, tier, regiao FROM times WHERE nome ILIKE ? ORDER BY nome",
            [f"%{busca}%"],
        ).fetchall()
    else:
        resultado = conexao.execute(
            "SELECT time_id, nome, tier, regiao FROM times ORDER BY nome"
        ).fetchall()
    conexao.close()
    return [
        {"time_id": r[0], "nome": r[1], "tier": r[2], "regiao": r[3]} for r in resultado
    ]


@app.get("/times/{time_id}")
def detalhe_time(time_id: int):
    """Resumo de um time: nome, total de partidas, vitórias."""
    conexao = duckdb.connect(CAMINHO_BANCO, read_only=True)

    time_info = conexao.execute(
        "SELECT nome, tier, regiao FROM times WHERE time_id = ?", [time_id]
    ).fetchone()
    if not time_info:
        conexao.close()
        raise HTTPException(status_code=404, detail="Time não encontrado")

    resumo = conexao.execute(
        """
        SELECT COUNT(*) as total,
               SUM(CASE WHEN radiant_team_id = ? AND radiant_win THEN 1
                        WHEN dire_team_id = ? AND NOT radiant_win THEN 1 ELSE 0 END) as vitorias
        FROM partidas
        WHERE radiant_team_id = ? OR dire_team_id = ?
    """,
        [time_id, time_id, time_id, time_id],
    ).fetchone()
    conexao.close()

    return {
        "time_id": time_id,
        "nome": time_info[0],
        "tier": time_info[1],
        "regiao": time_info[2],
        "total_partidas": resumo[0],
        "vitorias": resumo[1],
    }


class PerguntaInput(BaseModel):
    pergunta: str


@app.post("/perguntar")
def perguntar_ia(entrada: PerguntaInput):
    """Faz uma pergunta em linguagem natural pro agente text-to-SQL."""
    try:
        schema = descrever_schema()
        sql = gerar_sql(entrada.pergunta, schema)
        resultado = rodar_sql(sql)
        resposta = formatar_resposta(entrada.pergunta, sql, resultado)
        return {"pergunta": entrada.pergunta, "resposta": resposta}
    except Exception as erro:
        raise HTTPException(status_code=500, detail=str(erro))
