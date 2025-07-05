import re
from typing import List, Tuple

def is_title(line: str) -> bool:
    """Detecta se a linha parece um título ou subtítulo."""
    return (
        line.isupper() or
        re.match(r'^(CAP[IÍ]TULO|TÍTULO|SEÇÃO|ARTIGO|Art\.|\d+\.|\d+\))', line)
    )

def segment_by_structure(blocks: List[str]) -> List[Tuple[str, str]]:
    """
    Agrupa blocos em (subtitulo, parágrafo) baseado em detecção de título.
    Retorna uma lista de pares (contexto, parágrafo).
    """
    segmentos = []
    contexto_atual = "Sem Título"

    for bloco in blocks:
        linhas = bloco.split("\n")
        primeira = linhas[0].strip()

        if is_title(primeira):
            contexto_atual = primeira.strip()
            continue

        segmentos.append((contexto_atual, bloco.strip()))

    return segmentos

if __name__ == "__main__":
    import sys
    import json
    from extract_text import extract_text_blocks

    if len(sys.argv) != 2:
        print("Uso: python segment_blocks.py <arquivo.pdf>")
        exit(1)

    pdf_file = sys.argv[1]
    blocos = extract_text_blocks(pdf_file)
    segmentos = segment_by_structure(blocos)

    print(f"\n\nSegmentação completa: {len(segmentos)} pares (subtítulo, parágrafo).\n")
    for i, (contexto, par) in enumerate(segmentos):
        print(f"[{i+1}] {contexto}\n{par}\n---\n")
