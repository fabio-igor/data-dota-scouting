"""
Agente text-to-SQL: recebe uma pergunta em português, escreve a query SQL,
roda no banco de verdade, e responde em linguagem natural.

Uso: python src/ai/perguntar.py "quais heróis a LGD mais baniu contra o PlayTime?"
"""

import os
import sys

import duckdb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODELO = "openai/gpt-oss-20b:free"
CAMINHO_BANCO = "data/processed/scouting_platform.duckdb"

_cliente = None


def obter_cliente():
    """Cria o cliente da OpenAI só na primeira vez que for usado, não na
    importação do módulo — assim endpoints que não usam IA continuam
    funcionando mesmo se a chave estiver ausente ou inválida."""
    global _cliente
    if _cliente is None:
        _cliente = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
    return _cliente


def descrever_schema():
    conexao = duckdb.connect(CAMINHO_BANCO)
    tabelas = [r[0] for r in conexao.execute("SHOW TABLES").fetchall()]
    linhas = []
    for tabela in tabelas:
        colunas = conexao.execute(f"DESCRIBE {tabela}").fetchall()
        nomes_colunas = ", ".join(f"{c[0]} ({c[1]})" for c in colunas)
        linhas.append(f"- {tabela}: {nomes_colunas}")
    conexao.close()
    return "\n".join(linhas)


def gerar_sql(pergunta, schema):
    prompt_sistema = f"""Você é um especialista em SQL (dialeto DuckDB) para um banco de dados de scouting de Dota 2.

Schema disponível:
{schema}

Contexto importante:
- radiant_team_id/dire_team_id em 'partidas' identificam os dois times de cada partida
- radiant_win (booleano) diz se o time Radiant venceu
- time_id em outras tabelas (jogadores_partida, picks_bans, roshan_kills) identifica de qual time é aquele registro
- Para saber se um time X venceu uma partida: (radiant_team_id = X AND radiant_win) OR (dire_team_id = X AND NOT radiant_win)
- Nomes de time ficam na tabela 'times' (coluna nome), nomes de herói em 'herois' (coluna nome_localizado)
- IMPORTANTE: para buscar time ou herói pelo nome, NUNCA use igualdade exata (=). Use sempre ILIKE '%termo%' — o nome exato salvo no banco pode ser diferente do que a pergunta usa (ex: a pergunta diz "LGD", o banco tem "LGD Gaming"; a busca com ILIKE '%LGD%' encontra os dois)
- ATENÇÃO: existem MÚLTIPLOS times com "LGD" no nome no banco (incluindo duplicatas e times não relacionados, como times acadêmicos). Quando a pergunta for sobre "a LGD", "nosso time", ou "LGD Gaming" (o time principal que rastreamos), use time_id = 10150538 diretamente — NÃO busque por nome nesse caso específico, pois o nome é ambíguo. Para outros times (adversários), pode usar ILIKE normalmente.

Responda APENAS com a query SQL, sem explicação, sem markdown, sem ```. Só a query, pronta pra rodar."""

    resposta = obter_cliente().chat.completions.create(
        model=MODELO,
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": pergunta},
        ],
    )
    sql = resposta.choices[0].message.content.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql


def rodar_sql(sql):
    conexao = duckdb.connect(CAMINHO_BANCO)
    try:
        resultado = conexao.execute(sql).fetchdf()
        return resultado
    finally:
        conexao.close()


def formatar_resposta(pergunta, sql, resultado):
    prompt = f"""Pergunta original: {pergunta}

Query SQL executada: {sql}

Resultado (primeiras linhas):
{resultado.head(20).to_string()}

Responda a pergunta original em português, de forma natural e direta, baseado só nesse resultado."""

    resposta = obter_cliente().chat.completions.create(
        model=MODELO,
        messages=[{"role": "user", "content": prompt}],
    )
    return resposta.choices[0].message.content


def perguntar(pergunta, debug=False):
    schema = descrever_schema()
    sql = gerar_sql(pergunta, schema)
    if debug:
        print(f"SQL gerado:\n{sql}\n")

    resultado = rodar_sql(sql)
    if debug:
        print(f"{len(resultado)} linha(s) retornada(s)\n")

    resposta = formatar_resposta(pergunta, sql, resultado)
    print(resposta)


if __name__ == "__main__":
    argumentos = [a for a in sys.argv[1:] if a != "--debug"]
    modo_debug = "--debug" in sys.argv

    if not argumentos:
        print('Uso: python src/ai/perguntar.py "sua pergunta aqui" [--debug]')
        sys.exit(1)
    perguntar(argumentos[0], debug=modo_debug)
