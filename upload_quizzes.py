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

def gerar_titulo(id):
    id_formatado = id.upper().replace("PH", "PH - ")
    if "CIENCIAS" in id_formatado:
        return id_formatado.replace("CIENCIAS", "CIÊNCIAS")
    return id_formatado

def enviar_quiz(tema, subtema_id, perguntas):
    data = {
        "tema": tema,
        "titulo": subtema_id,
        "ativo": True,
        "perguntas": perguntas
    }

    response = requests.post(f"{SUPABASE_URL}/rest/v1/quizzes", headers=HEADERS, data=json.dumps(data))
    if response.status_code == 201:
        print(f"✅ Enviado com sucesso: {tema} / {subtema_id}")
    elif response.status_code == 409:
        print(f"⚠️ Já existe: {tema} / {subtema_id} (considere usar UPSERT)")
    else:
        print(f"❌ Erro ao enviar {subtema_id}: {response.status_code} - {response.text}")

if __name__ == "__main__":
    try:
        with open("questions.json", "r", encoding="utf-8") as f:
            estrutura = json.load(f)
            for tema, subtemas in estrutura.items():
                for subtema_id, perguntas in subtemas.items():
                    enviar_quiz(tema, subtema_id, perguntas)
    except FileNotFoundError:
        print("❌ Arquivo questions.json não encontrado.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao interpretar o JSON: {e}")
        sys.exit(1)