import os
import pdfplumber
import openai
import json
from typing import List

# Carrega a chave da OpenAI da variável de ambiente
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_blocks_from_pdf(pdf_path: str, block_size: int = 500) -> List[str]:
    with pdfplumber.open(pdf_path) as pdf:
        textos = []
        for page in pdf.pages:
            try:
                texto = page.extract_text()
                if texto:
                    textos.append(texto)
            except Exception as e:
                print(f"Erro ao extrair texto de uma página: {e}")
        full_text = " ".join(textos)

    words = full_text.split()
    blocks = [" ".join(words[i:i + block_size]) for i in range(0, len(words), block_size)]
    return blocks

def generate_questions_from_block(block_text: str, n_questions: int = 5) -> List[dict]:
    prompt = (
        f"Leia o texto abaixo e elabore {n_questions} questões de múltipla escolha com 4 alternativas cada, "
        f"indicando a resposta correta com base no índice da opção correta (0 a 3). "
        f"Formate como uma lista JSON com o seguinte modelo:\n"
        f'[{{ "question": "...", "options": ["...", "...", "...", "..."], "answer": 2 }}]\n\n'
        f"Texto:\n{block_text}\n\n"
    )

    response = openai.ChatCompletion.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    content = response.choices.[0].message.content

    try:
        start = content.find('[')
        end = content.rfind(']') + 1
        questions = json.loads(content[start:end])
        return questions
    except Exception as e:
        print("Erro ao interpretar resposta do modelo:", e)
        return []

def process_all_pdfs(root_folder: str, output_file: str):
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
                questions = generate_questions_from_block(block)
                all_questions.extend(questions)

        if tema not in result:
            result[tema] = {}
        result[tema][subtema] = all_questions

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Arquivo {output_file} gerado com sucesso.")

# Execução direta pelo terminal
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Uso: python process_folder.py <pasta_raiz_dos_pdfs> <arquivo_saida.json>")
    else:
        pasta_raiz = sys.argv[1]
        arquivo_saida = sys.argv[2]
        process_all_pdfs(pasta_raiz, arquivo_saida)