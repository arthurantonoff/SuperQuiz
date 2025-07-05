import json
import re
from typing import List, Dict
from difflib import SequenceMatcher

def is_valid_question(q: Dict) -> bool:
    """Verifica estrutura básica da pergunta."""
    texto = q.get("question", "")
    if len(texto.split()) < 4:
        return False
    if not texto.endswith("?"):
        return False
    if any(x in texto.lower() for x in ["crie", "gere", "baseado", "elabore"]):
        return False
    return True

def is_similar(q1: str, q2: str, threshold: float = 0.85) -> bool:
    """Verifica similaridade entre perguntas."""
    return SequenceMatcher(None, q1, q2).ratio() > threshold

def remove_duplicates(questions: List[Dict]) -> List[Dict]:
    """Remove perguntas muito semelhantes."""
    filtradas = []
    for q in questions:
        if not is_valid_question(q):
        
            continue
        if any(is_similar(q["question"], f["question"]) for f in filtradas):
            continue
        filtradas.append(q)
    return filtradas

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Uso: python validate_questions.py <entrada.json> <saida.json>")
        exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    filtradas = remove_duplicates(data)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(filtradas, f, indent=2, ensure_ascii=False)

    print(f"Validação completa: {len(filtradas)} questões mantidas em {output_file}.")
