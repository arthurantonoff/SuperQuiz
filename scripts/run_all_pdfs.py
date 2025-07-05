import os
import json
import traceback
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
            if file.lower().endswith(".pdf"):
                pdfs.append(os.path.join(dirpath, file))
    return pdfs

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    base_pdfs = os.path.abspath(os.path.join(root_dir, "..", "pdfreader", "pdfs"))
    output_file = os.path.abspath(os.path.join(root_dir, "..", "questions.json"))

    print("Diretório atual:", os.getcwd())
    print("Verificando PDFs em:", base_pdfs)

    if not os.path.exists(base_pdfs):
        print("❌ Pasta de PDFs não encontrada.")
        return

    arquivos = encontrar_pdfs(base_pdfs)
    print(f"Encontrados {len(arquivos)} PDFs para processar.\n")

    resultado_final = {}

    for pdf in arquivos:
        print(f"▶️ Processando: {pdf}")
        try:
            estrutura = pipeline(pdf)
            merge_nested(resultado_final, estrutura)
        except Exception as e:
            print(f"❌ Erro ao processar {pdf}: {e}")
            traceback.print_exc()

    if not resultado_final:
        print("⚠️ Nenhum dado gerado. Verifique os PDFs.")
        return

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(resultado_final, f, indent=2, ensure_ascii=False)
    print(f"\n {resultado_final}")
    print(f"\n✅ Todos os PDFs foram processados. Total de temas: {len(resultado_final)}")
    print(f"Arquivo salvo em: {output_file}")

if __name__ == "__main__":
    main()