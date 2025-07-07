import os
import re
from typing import List, Tuple, Dict

USE_OPENAI = os.getenv("USE_OPENAI", "false").lower() == "true"

if USE_OPENAI:
    print("Usando OpenAI")
    import openai
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_openai(prompt: str, max_tokens: int = 512) -> str:
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {
                "role": "system",
                "content": (
                    "Você é um gerador de questões objetivas de múltipla escolha com 4 alternativas. "
                    "Sua função inclui: análise de conteúdo, formulação interpretativa, construção linguística clara e revisão pedagógica. "
                    "Toda pergunta deve ser tecnicamente precisa, didaticamente eficaz e linguisticamente revisada. Responda sempre no formato JSON."
                )
            },
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def parse_json_block(text: str) -> Dict:
    try:
        import json
        data = json.loads(text)
        if all(k in data for k in ["question", "options", "answer"]):
            return data
    except Exception:
        pass
    return {
        "question": "Erro na geração.",
        "options": ["A", "B", "C", "D"],
        "answer": 0
    }

def generate_question_block(context: str, text_block: str) -> Dict:
    text_block = " ".join(text_block.split()[:450])
    context = " ".join(context.split()[:50])

    prompt = (
        f"[TÍTULO]: {context}\n"
        f"[TEXTO]: {text_block}\n\n"
        f"[INSTRUÇÃO]: Leia o conteúdo acima com atenção. Com base nele, elabore uma pergunta objetiva de múltipla escolha com as seguintes características:\n"
        f"1. A pergunta deve explorar um conceito central, inferência ou aplicação;\n"
        f"2. As quatro alternativas devem ser plausíveis e no mesmo nível linguístico;\n"
        f"3. Indique a resposta correta no índice da lista;\n"
        f"4. Use linguagem didática e evite copiar frases literais do texto;\n"
        f"5. O formato da resposta deve ser exatamente:\n\n"
        f'{{\n  "question": "...",\n  "options": ["...", "...", "...", "..."],\n  "answer": 0\n}}\n'
    )
    resposta = ask_openai(prompt)
    return parse_json_block(resposta)

def generate_all(segments: List[Tuple[str, str]]) -> List[Dict]:
    questions = []
    for i, (context, text_block) in enumerate(segments):
        print(f"Gerando questão {i+1}/{len(segments)}...")
        try:
            q = generate_question_block(context, text_block)
            questions.append(q)
        except Exception as e:
            print(f"Erro ao gerar questão no bloco {i+1}: {e}")
    return questions

if __name__ == "__main__":
    import sys
    import json
    from scripts.extract_text import extract_text_blocks
    from scripts.segment_by_context import extract_context_blocks

    if len(sys.argv) != 3:
        print("Uso: python generate_questions.py <arquivo.pdf> <saida.json>")
        exit(1)

    pdf_file = sys.argv[1]
    output_file = sys.argv[2]

    lines = extract_text_blocks(pdf_file)
    segments = extract_context_blocks(lines)
    questions = generate_all(segments)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)

    print(f"\nGeração completa: {len(questions)} questões salvas em {output_file}.")