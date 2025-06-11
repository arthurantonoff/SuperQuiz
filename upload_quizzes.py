import json
import requests
import os
import sys

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Erro: SUPABASE_URL ou SUPABASE_KEY não encontrados no ambiente.")
    sys.exit(1)

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def enviar_quiz(titulo, perguntas):
    data = {
        "titulo": titulo,
        "ativo": True,
        "perguntas": perguntas
    }

    response = requests.post(f"{SUPABASE_URL}/rest/v1/quizzes", headers=HEADERS, data=json.dumps(data))
    if response.status_code == 201:
        print(f"✅ Enviado com sucesso: {titulo}")
    elif response.status_code == 409:
        print(f"⚠️ Já existe: {titulo} (considere usar UPSERT)")
    else:
        print(f"❌ Erro ao enviar {titulo}: {response.status_code} - {response.text}")

if __name__ == "__main__":
    try:
        with open("questions.json", "r", encoding="utf-8") as f:
            estrutura = json.load(f)
            for titulo, subtemas in estrutura.items():
                for subtema, perguntas in subtemas.items():
                    enviar_quiz(titulo, perguntas)
    except FileNotFoundError:
        print("❌ Arquivo questions.json não encontrado.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao interpretar o JSON: {e}")
        sys.exit(1)