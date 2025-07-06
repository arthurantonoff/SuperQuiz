import re
from typing import List, Tuple

try:
    import spacy
    nlp = spacy.load("pt_core_news_sm")
except Exception:
    nlp = None  # spaCy opcional se não instalado

def is_context_by_heuristics(line: str) -> bool:
    """
    Detecta títulos com base em regras universais (semântica neutra):
    - Maiúsculas
    - Curto e capitalizado
    - Numeração (ex: 1.1 Tópico)
    """
    line = line.strip()
    return (
        len(line) >= 5 and
        len(line.split()) <= 8 and
        (
            line.isupper() or
            line.istitle() or
            bool(re.match(r'^\d+(\.\d+)*\s', line))
        )
    )

def is_context_by_nlp(line: str) -> bool:
    """
    Usa NLP (spaCy) para verificar se a linha é majoritariamente nominal
    """
    if not nlp:
        return False
    doc = nlp(line)
    tokens = [t for t in doc if not t.is_stop and t.is_alpha]
    return (
        len(tokens) >= 2 and
        all(t.pos_ in {"NOUN", "PROPN", "ADJ"} for t in tokens)
    )

def is_probable_context(line: str) -> bool:
    """
    Combina heurística + NLP (se disponível) para decidir se é um título de contexto
    """
    return is_context_by_heuristics(line) or is_context_by_nlp(line)

def extract_context_blocks(lines: List[str], max_paragraphs: int = 4) -> List[Tuple[str, str]]:
    """
    Agrupa parágrafos sob o último contexto identificado. Contexto detectado dinamicamente.
    Retorna lista de tuplas (contexto, parágrafos agrupados)
    """
    context = None
    current = []
    blocks = []
    paragraph_count = 0

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if is_probable_context(line):
            if context and current:
                blocks.append((context, " ".join(current)))
            context = line.strip()
            current = []
            paragraph_count = 0
        else:
            current.append(line)
            paragraph_count += 1
            if paragraph_count >= max_paragraphs:
                if context and current:
                    blocks.append((context, " ".join(current)))
                current = []
                paragraph_count = 0

    if context and current:
        blocks.append((context, " ".join(current)))

    return blocks