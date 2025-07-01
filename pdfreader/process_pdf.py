import pdfplumber
import openai
import json
import os
from typing import List

# Carrega a chave da OpenAI da variável de ambiente
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_blocks_from_pdf(pdf_path: str, block_size: int = 500) -> List[str]:
    """Extrai texto do PDF e divide em blocos de ~500 palavras"""
    with pdfplumber.open(pdf_path) as pdf:
        full_text = " ".join([page.extract_text() for page in pdf if page.extract_text()])
    words = full_text.split()
    blocks = [" ".join(words[i:i+block_size]) for i in range(0, len(words), block_size)]
    return blocks

def generate_questions_from_block(block_text: str, n_questions: int = 5) -> List[dict]:
    """Gera questões usando LLM com base em um bloco de texto"""
    prompt = (
        f"Leia o texto abaixo e elabore {n_questions} questões de múltipla escolha com 4 alternativas cada, "
        f"indicando a resposta correta com base no índice da opção correta (0 a 3). "
        f"Formate como uma lista JSON com o seguinte modelo:\n"
        f'[{{ "question": "...", "options": ["...", "...", "...", "..."], "answer": 2 }}]\n\n'
        f"Texto:\n{block_text}\n\n"
    )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    content = response['choices'][0]['message']['content']

    try:
        # Extrai o trecho JSON válido da resposta
        start = content.find('[')
        end = content.rfind(']') + 1
        questions = json.loads(content[start:end])
        return questions
    except Exception as e:
        print("Erro ao interpretar a resposta do LLM:", e)
        return []

def process_pdf_to_questions(pdf_path: str, output_json: str = "questions.json"):
    """Processa o PDF e salva todas as questões no formato JSON"""
    print(f"Processando: {pdf_path}")
    blocks = extract_blocks_from_pdf(pdf_path)
    all_questions = []

    for i, block in enumerate(blocks):
        print(f"Gerando perguntas para bloco {i+1} de {len(blocks)}...")
        questions = generate_questions_from_block(block)
        all_questions.extend(questions)

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(all_questions, f, indent=2, ensure_ascii=False)

    print(f"{len(all_questions)} questões salvas em '{output_json}'")

# Para uso via linha de comando
if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 2:
        input_pdf = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) >= 3 else "questions.json"
        process_pdf_to_questions(input_pdf, output_file)
    else:
        print("Uso: python process_pdf.py arquivo.pdf [saida.json]")