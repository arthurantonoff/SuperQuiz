import random
import os
from typing import List, Tuple, Dict

# Verifica se deve usar OpenAI
USE_OPENAI = os.getenv("USE_OPENAI", "false").lower() == "true"
#USE_OPENAI = False

if USE_OPENAI:
    print("Usando OpenAI")
    import openai
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

else:
    from transformers import pipeline
    generator = pipeline("text2text-generation",
                      model="google/flan-t5-large",
                      tokenizer="google/flan-t5-large",
                      truncation=True
                      )

def ask_openai(prompt: str, max_tokens: int = 512) -> str:
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": "Você é um gerador de questões objetivas de múltipla escolha com 4 alternativas, com função completa de análise, formulação e revisão. Seu comportamento inclui: interpretar o conteúdo com profundidade, extrair ideias essenciais, formular perguntas com clareza e desafio adequado, e revisar linguisticamente para eliminar ambiguidade, inconsistência e erro conceitual. Toda questão deve ser construída com base em domínio do conteúdo, precisão técnica e foco didático."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def rotate_options(options: list) -> (list, int):
    n = random.randint(0, 3)
    rotated = options[n:] + options[:n]
    correct_index = (0 - n) % 4
    return rotated, correct_index

def generate_question_block(context: str, paragraph: str) -> Dict:
    paragraph = " ".join(paragraph.split()[:500])
    context = " ".join(paragraph.split()[:50])
    prompt_q = (
        f"[TÓPICO]: {context}\n"
        f"[TEXTO]: {paragraph}\n\n"
        f"[PERGUNTA]: Leia atentamente o texto abaixo. Com base nele, elabore uma pergunta objetiva de múltipla escolha que: (1) reflita um conceito central ou inferência válida; (2) seja clara, direta e bem formulada; (3) esteja escrita com linguagem compatível com material didático; e (4) termine com ponto de interrogação. Não copie frases literais do texto. Não gere perguntas vagas, óbvias ou genéricas. Explore o conteúdo de forma aplicada, interpretativa ou conceitual, garantindo um nível mínimo de desafio."
    )
    question = ask_openai(prompt_q) if USE_OPENAI else generator(prompt_q, max_new_tokens=80,truncation=True)[0]['generated_text'].strip()

    prompt_a = (
        f"[TÓPICO]: {context}\n"
        f"[TEXTO]: {paragraph}\n\n"
        
        f"[RESPOSTA]: Indique a alternativa correta que responde com exatidão à pergunta. Esta resposta deve ser inequivocamente verdadeira com base no texto. Certifique-se de que não haja espaço para ambiguidade ou múltiplas interpretações. Ela deve refletir o conteúdo de forma precisa, sem erro factual ou exagero interpretativo. Evite usar palavras vagas ou absolutas sem base no texto. A resposta correta será a opção correta no conjunto final de alternativas."
    )
    correct = ask_openai(prompt_a) if USE_OPENAI else generator(prompt_a, max_new_tokens=60)[0]['generated_text'].strip()

    prompt_d = (
        f"[TÓPICO]: {context}\n"
        f"[TEXTO]: {paragraph}\n\n"

        f"[ERRADAS]: Escreva três alternativas incorretas plausíveis. Elas devem (1) parecer corretas à primeira vista; (2) manter o mesmo nível linguístico e temático da alternativa certa; (3) estar tecnicamente erradas ou conceitualmente incorretas; e (4) não repetir entre si nem contradizer a alternativa correta de forma óbvia. Use separador '||' entre elas. As alternativas erradas devem confundir quem leu o texto com superficialidade, mas não enganar o leitor bem preparado."
    )
    raw_distractors = ask_openai(prompt_d) if USE_OPENAI else generator(prompt_d, max_new_tokens=80)[0]['generated_text']
    distractors = [d.strip() for d in raw_distractors.split("||") if d.strip()][:3]
    while len(distractors) < 3:
        distractors.append("Alternativa incorreta")

    all_options, answer_index = rotate_options([correct] + distractors)

    return {
        "question": question,
        "options": all_options,
        "answer": answer_index
    }

def generate_all(segments: List[Tuple[str, str]]) -> List[Dict]:
    questions = []
    for i, (context, paragraph) in enumerate(segments):
        print(f"Gerando questão {i+1}/{len(segments)}...")
        try:
            q = generate_question_block(context, paragraph)
            questions.append(q)
        except Exception as e:
            print(f"Erro ao gerar questão no bloco {i+1}: {e}")
    return questions

if __name__ == "__main__":
    import sys
    import json
    from extract_text import extract_text_blocks
    from segment_blocks import segment_by_structure

    if len(sys.argv) != 3:
        print("Uso: python generate_questions.py <arquivo.pdf> <saida.json>")
        exit(1)

    pdf_file = sys.argv[1]
    output_file = sys.argv[2]

    blocks = extract_text_blocks(pdf_file)
    segments = segment_by_structure(blocks)
    questions = generate_all(segments)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)

    print(f"\nGeração completa: {len(questions)} questões salvas em {output_file}.")