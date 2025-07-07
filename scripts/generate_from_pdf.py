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

def gerar_questoes(texto: str, qtd: 40, max_tokens: int = 2*2048) -> str:
    """Envia o texto para a API da OpenAI e solicita questões formatadas em JSON."""
    prompt = (
        f"[TEXTO]: {texto}\n\n"
        f"[INSTRUÇÃO]: Com base no conteúdo acima, elabore {qtd} questões objetivas de múltipla escolha com 4 alternativas cada, seguindo rigorosamente os critérios abaixo:\n\n"
        f"1. Cada pergunta deve explorar um conceito central, inferência interpretativa ou aplicação prática relevante do texto.\n"
        f"2. As alternativas devem ser claras, plausíveis, bem escritas e no mesmo nível técnico e linguístico.\n"
        f"3. Apenas uma alternativa deve estar correta (sem ambiguidade). As erradas devem parecer críveis.\n"
        f"4. Não copie frases literais. Reformule com linguagem didática, técnica e acessível.\n"
        f"5. Evite perguntas vagas, genéricas, excessivamente factuais ou puramente memorísticas.\n"
        f"6. Mantenha um nível adequado de desafio, como em provas da PF, PRF, CESPE ou FCC.\n"
        f"7. Ao final, o resultado deve estar exatamente neste formato JSON:\n\n"
        f"[\n"
        f"  {{\n"
        f"    \"question\": \"Enunciado claro e objetivo da pergunta\",\n"
        f"    \"options\": [\"Alternativa A\", \"Alternativa B\", \"Alternativa C\", \"Alternativa D\"],\n"
        f"    \"answer\": índice_da_opção_correta (0 a 3)\n"
        f"  }},\n"
        f"  ...\n"
        f"]"
    )

    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {
                "role": "system",
                "content": (
                    "Você é um gerador avançado de questões de concursos públicos. "
                    "Sua missão é interpretar textos com profundidade e gerar questões objetivas de múltipla escolha (4 alternativas), "
                    "bem formuladas, desafiadoras e didaticamente eficientes. Suas questões devem seguir critérios técnicos rigorosos, "
                    "com clareza, precisão e coerência pedagógica. Você também é responsável por revisar linguisticamente cada item, "
                    "evitando ambiguidade, erros conceituais ou alternativas mal escritas. O retorno deve estar 100% no formato JSON especificado."
                )
            },
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
    resposta = gerar_questoes(texto_completo, qtd=40)

    print("💾 Salvando questões...")
    salvar_questoes_em_json(resposta, output_json)