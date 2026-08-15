"""
Sanity check: confirma que a chave do OpenRouter funciona antes de
construir o agente de verdade.
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

chave = os.getenv("OPENROUTER_API_KEY")
if not chave:
    print(
        "OPENROUTER_API_KEY não encontrada. Confere se o .env está na raiz do projeto."
    )
    exit(1)

cliente = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=chave,
)

resposta = cliente.chat.completions.create(
    model="openai/gpt-oss-20b:free",
    messages=[
        {"role": "user", "content": "Responda só 'OK' se você recebeu essa mensagem."}
    ],
)

print("Resposta do modelo:", resposta.choices[0].message.content)
