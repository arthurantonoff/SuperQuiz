import os
import pdfplumber
import json
import random
from typing import List
from transformers import pipeline

# Inicializa o modelo Hugging Face (Flan-T5 Base)
generator = pipeline("text2text-generation", model="google/flan-t5-base")

def extract_blocks_from_pdf(pdf_path: str, block_size: int = 500) -> List[str]:
    """Extrai texto do PDF em blocos de aproximadamente 500 palavras"""
    with pdfplumber.open(pdf_path) as pdf:
        full_text = " ".join([page.extract_text() for page in pdf if page.extract_text()])
    words = full_text.split()
    blocks = [" ".join(words[i:i + block_size]) for i in range(0, len(words), block_size)]
    return blocks

def rotate_options(options: list) -> (list, int):
    """Desloca as opções aleatoriamente e retorna nova posição da correta"""
    n = random.randint(0, 3)
    rotated = options[n:] + options[:n]
    correct_index = (0 - n) % 4
    return rotated, correct_index

def generate_question_and_options(block_text: str) -> dict:
    """Gera pergunta, resposta correta, três erradas e embaralha tudo"""
    prompt_q = f"Crie uma pergunta objetiva com base no seguinte texto:\n{block_text[:800]}"
    question = generator(prompt_q, max_new_tokens=80)[0]['generated_text'].strip()

    prompt_a = f"Com base no texto abaixo, forneça a resposta correta para uma pergunta objetiva:\n{block_text[:800]}"
    correct = generator(prompt_a, max_new_tokens=60)[0]['generated_text'].strip()

    prompt_d = f"Com base no texto abaixo, forneça três respostas erradas plausíveis para uma pergunta objetiva, separadas por '||':\n{block_text[:800]}"
    raw_distractors = generator(prompt_d, max_new_tokens=80)[0]['generated_text']
    distractors = [d.strip() for d in raw_distractors.split("||") if d.strip()][:3]

    while len(distractors) < 3:
        distractors.append("Alternativa incorreta")

    all_options, answer_index = rotate_options([correct] + distractors)

    return {
        "question": question,
        "options": all_options,
        "answer": answer_index
    }

def process_all_pdfs(root_folder: str, output_file: str):
    """Percorre todas as pastas TEMA/SUBTEMA, processa PDFs e salva em JSON"""
    result = {}

    for dirpath, _, filenames in os.walk(root_folder):
        pdfs = [f for f in filenames if f.endswith(".pdf")]
        if not pdfs:
            continue

        parts = dirpath.split(os.sep)
        if len(parts) < 3:
            print(f"Pasta ignorada (esperado pelo menos TEMA/SUBTEMA): {dirpath}")
            continue

        tema = parts[-2]
        subtema = parts[-1]
        all_questions = []

        print(f"Processando tema: {tema} / subtema: {subtema}")

        for pdf_file in pdfs:
            pdf_path = os.path.join(dirpath, pdf_file)
            print(f" → PDF: {pdf_file}")
            blocks = extract_blocks_from_pdf(pdf_path)
            for block in blocks:
                question_obj = generate_question_and_options(block)
                all_questions.append(question_obj)

        if tema not in result:
            result[tema] = {}
        result[tema][subtema] = all_questions

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Arquivo {output_file} gerado com sucesso.")

# Execução via terminal
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Uso: python process_folder.py <pasta_raiz_dos_pdfs> <arquivo_saida.json>")
    else:
        pasta_raiz = sys.argv[1]
        arquivo_saida = sys.argv[2]
        process_all_pdfs(pasta_raiz, arquivo_saida)