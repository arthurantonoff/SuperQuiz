import os
import sys
import json
from extract_text import extract_text_blocks
from segment_blocks import segment_by_structure
from generate_questions import generate_all
from validate_questions import remove_duplicates
from format_questions_json import infer_tema_subtema, format_to_nested_structure

def pipeline(pdf_path: str, output_path: str):
    print("\n🟡 Etapa 1: Extraindo texto limpo...")
    blocks = extract_text_blocks(pdf_path)

    print("\n🟡 Etapa 2: Segmentando blocos por título e parágrafo...")
    segments = segment_by_structure(blocks)

    print("\n🟡 Etapa 3: Gerando questões com IA...")
    raw_questions = generate_all(segments)

    print("\n🟡 Etapa 4: Validando questões...")
    valid_questions = remove_duplicates(raw_questions)

    print("\n🟡 Etapa 5: Formatando para estrutura final...")
    tema, subtema = infer_tema_subtema(pdf_path)
    estrutura = format_to_nested_structure(valid_questions, tema, subtema)

    print(f"\n💾 Salvando arquivo: {output_path}")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(estrutura, f, indent=2, ensure_ascii=False)

    print(f"✅ Pipeline finalizado com sucesso! {len(valid_questions)} questões salvas.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python pipeline_main.py <arquivo.pdf> <saida.json>")
        sys.exit(1)

    pdf = sys.argv[1]
    saida = sys.argv[2]
    pipeline(pdf, saida)
