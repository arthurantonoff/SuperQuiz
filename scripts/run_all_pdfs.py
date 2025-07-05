import os
import json
from pipeline_main import pipeline

def merge_nested(base: dict, novo: dict):
    for tema in novo:
        if tema not in base:
            base[tema] = novo[tema]
        else:
            for subtema in novo[tema]:
                if subtema not in base[tema]:
                    base[tema][subtema] = novo[tema][subtema]
                else:
                    base[tema][subtema].extend(novo[tema][subtema])

def encontrar_pdfs(pasta_base: str):
    pdfs = []
    for dirpath, _, filenames in os.walk(pasta_base):
        for file in filenames:
            if file.endswith(".pdf"):
                pdfs.append(os.path.join(dirpath, file))
    return pdfs

def main():
    base_pdfs = "pdfreader/pdfs"
    output_file = "questions.json"
    resultado_final = {}

    arquivos = encontrar_pdfs(base_pdfs)
    print(f"Encontrados {len(arquivos)} PDFs para processar.\n")

    for pdf in arquivos:
        print(f"▶️ Processando: {pdf}")
        try:
            estrutura = pipeline(pdf)
            merge_nested(resultado_final, estrutura)
        except Exception as e:
            print(f"Erro ao processar {pdf}: {e}")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(resultado_final, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Todos os PDFs foram processados. Total de temas: {len(resultado_final)}")

if __name__ == "__main__":
    main()