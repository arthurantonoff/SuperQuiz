import os
import json
from typing import List, Dict

def infer_tema_subtema(path: str) -> (str, str):
    """Extrai tema e subtema do caminho do PDF."""
    partes = path.replace("\\", "/").split("/")
    tema = partes[-3] if len(partes) >= 3 else "GERAL"
    subtema = partes[-2] if len(partes) >= 2 else "SEM SUBTEMA"
    return tema.strip(), subtema.strip()

def format_to_nested_structure(questions: List[Dict], tema: str, subtema: str) -> Dict:
    return { tema: { subtema: questions } }

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        print("Uso: python format_questions_json.py <entrada.json> <pdf_path> <saida.json>")
        exit(1)

    entrada = sys.argv[1]  # ex: perguntas_validadas.json
    pdf_path = sys.argv[2] # ex: pdfreader/pdfs/PF2025/Direito Penal/texto.pdf
    saida = sys.argv[3]    # ex: questions.json

    with open(entrada, "r", encoding="utf-8") as f:
        questions = json.load(f)

    tema, subtema = infer_tema_subtema(pdf_path)
    nested = format_to_nested_structure(questions, tema, subtema)

    with open(saida, "w", encoding="utf-8") as f:
        json.dump(nested, f, indent=2, ensure_ascii=False)

    print(f"Arquivo salvo em {saida} com TEMA: '{tema}' e SUBTEMA: '{subtema}'.")
