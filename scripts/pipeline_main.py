import os
import json
import traceback
from scripts.extract_text import extract_text_blocks
from scripts.segment_by_context import extract_context_blocks
from scripts.generate_questions import generate_all
from scripts.validate_questions import remove_duplicates


def pipeline(pdf_path: str) -> dict:
    print(f"📄 Iniciando pipeline para: {pdf_path}")

    # Etapa 1: Extração de texto
    print("🔹 Etapa 1: Extraindo texto do PDF...")
    try:
        raw_lines = extract_text_blocks(pdf_path)
    except Exception as e:
        raise RuntimeError(f"Erro na extração do PDF: {e}")

    # Etapa 2: Segmentação semântica (estilo Chefe)
    print("🔹 Etapa 2: Segmentando em blocos por contexto...")
    segments = extract_context_blocks(raw_lines)

    if not segments:
        raise ValueError("Nenhum bloco segmentado encontrado. Verifique o PDF.")

    # Etapa 3: Geração de perguntas via OpenAI
    print("🔹 Etapa 3: Gerando questões com IA...")
    raw_questions = generate_all(segments)

    # Etapa 4: Validação das questões
    print("🔹 Etapa 4: Validando questões...")
    valid_questions = remove_duplicates(raw_questions)

    # Etapa 5: Estrutura final (tema/subtema)
    print("🔹 Etapa 5: Formatando para estrutura final...")
    tema = os.path.normpath(pdf_path).split(os.sep)[-3]  # ex: PF2025
    subtema = os.path.normpath(pdf_path).split(os.sep)[-2]  # ex: Direito Penal

    estrutura = {
        tema: {
            subtema: valid_questions
        }
    }

    print(f"✅ Pipeline concluído para: {pdf_path}\n")
    return estrutura