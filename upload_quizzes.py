import json
import requests
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
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

def enviar_quiz(id, perguntas):
    data = {
        "id": id,
        "titulo": gerar_titulo(id),
        "ativo": True,
        "perguntas": perguntas
    }

    response = requests.post(f"{SUPABASE_URL}/rest/v1/quizzes", headers=HEADERS, data=json.dumps(data))
    if response.status_code == 201:
        print(f"Enviado: {id}")
    elif response.status_code == 409:
        print(f"Já existe: {id} (considere usar UPSERT)")
    else:
        print(f"Erro ao enviar {id}: {response.status_code} - {response.text}")

if __name__ == "__main__":
    with open("questions.json", "r", encoding="utf-8") as f:
        base = json.load(f)
        for tema_id, perguntas in base.items():
            enviar_quiz(tema_id, perguntas)
