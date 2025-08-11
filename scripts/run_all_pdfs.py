import os
import sys
import json
import subprocess

def encontrar_pdfs(pasta_base: str):
    pdfs = []
    for dirpath, _, filenames in os.walk(pasta_base):
        for file in filenames:
            if file.lower().endswith(".pdf"):
                pdfs.append(os.path.join(dirpath, file))
    return pdfs

def processar_pdf_com_openai(pdf_path: str, temp_json: str):
    try:
        subprocess.run(
            ["python", "scripts/generate_from_pdf.py", pdf_path, temp_json],
            check=True
        )
        with open(temp_json, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Erro ao processar {pdf_path}: {e}")
        return []

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    pasta_pdfs = os.path.join(base_dir, "pdfreader", "pdfs")
    temp_file = os.path.join(base_dir, "saida_temp.json")
    estrutura_completa = {}

    arquivos = encontrar_pdfs(pasta_pdfs)
    if not arquivos:
        print("⚠️ Nenhum PDF encontrado.")
        return

    for caminho in arquivos:
        print(f"\n📄 Processando: {caminho}")
        tema = os.path.normpath(caminho).split(os.sep)[-3]
        subtema = os.path.normpath(caminho).split(os.sep)[-2]

        questoes = processar_pdf_com_openai(caminho, temp_file)

        if not questoes:
            print("⚠️ Nenhuma questão gerada.")
            continue

        if tema not in estrutura_completa:
            estrutura_completa[tema] = {}
        if subtema not in estrutura_completa[tema]:
            estrutura_completa[tema][subtema] = []

        estrutura_completa[tema][subtema].extend(questoes)

    return estrutura_completa

if __name__ == "__main__":
    resultado = main()
    if resultado:
        print("\n✅ Processamento final concluído. Use pipeline_main.py para salvar o questions.json.")