import pdfplumber
import os
import re
from typing import List

def clean_line(line: str) -> str:
    """Remove linhas com ruídos comuns"""
    line = line.strip()
    # Remove sequências inúteis ou nomes repetidos
    if re.match(r'^[\s\W\d]{3,}$', line):
        return ''
    if any(x in line.lower() for x in ["presidente:", "vice-presidente:", "livro eletr\u00f4nico", "www", "fb.com", "instagram"]):
        return ''
    if len(line) <= 2:
        return ''
    return line

def extract_text_blocks(pdf_path: str) -> List[str]:
    """
    Extrai texto limpo do PDF, retorna blocos separados por parágrafos significativos.
    """
    blocks = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                lines = [clean_line(ln) for ln in text.split("\n")]
                paragraph = ""
                for line in lines:
                    if not line:
                        if paragraph.strip():
                            blocks.append(paragraph.strip())
                            paragraph = ""
                        continue
                    paragraph += " " + line
                if paragraph.strip():
                    blocks.append(paragraph.strip())
    except Exception as e:
        print(f"Erro ao processar {pdf_path}: {e}")

    return blocks

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Uso: python extract_text.py <arquivo.pdf>")
        exit(1)

    pdf_file = sys.argv[1]
    blocos = extract_text_blocks(pdf_file)
    print(f"\n\nExtração completa: {len(blocos)} blocos encontrados.\n")
    for i, bloco in enumerate(blocos):
        print(f"[Bloco {i+1}]\n{bloco}\n---\n")
