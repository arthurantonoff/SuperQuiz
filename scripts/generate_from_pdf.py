import os
import json
import openai
import pdfplumber

# Configuração da API
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_clean_text(pdf_path: str) -> str:
    """Extrai texto limpo de um PDF inteiro."""
    full_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text.append(text.strip())
    return "\n".join(full_text)

def gerar_questoes(texto: str, qtd: int = 5, max_tokens: int = 2048) -> str:
    """Envia o texto para a API da OpenAI e solicita questões formatadas em JSON."""
    prompt = (
        f"[TEXTO]: {texto}\n\n"
        f"[INSTRUÇÃO]: Com base no texto acima, elabore {qtd} questões objetivas de múltipla escolha com 4 alternativas cada. "
        f"Cada questão deve explorar um conceito central, ter linguagem didática, nível interpretativo, e vir formatada exatamente assim:\n\n"
        f"[\n  {{\n    \"question\": \"...\",\n    \"options\": [\"...\", \"...\", \"...\", \"...\"],\n    \"answer\": 0\n  }}, ...\n]"
    )

    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": "Você é um gerador didático de questões objetivas com 4 alternativas."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content.strip()

def salvar_questoes_em_json(questoes_json: str, output_path: str):
    try:
        data = json.loads(questoes_json)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Questões salvas em {output_path}")
    except Exception as e:
        print("❌ Erro ao salvar JSON:", e)

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Uso: python generate_from_pdf.py <arquivo.pdf> <saida.json>")
        exit(1)

    pdf_path = sys.argv[1]
    output_json = sys.argv[2]

    print("🔍 Extraindo texto do PDF...")
    texto_completo = extract_clean_text(pdf_path)

    print("🤖 Enviando para o OpenAI...")
    resposta = gerar_questoes(texto_completo, qtd=5)

    print("💾 Salvando questões...")
    salvar_questoes_em_json(resposta, output_json)