import os
import json
from scripts import run_all_pdfs

def salvar_questions_json(estrutura: dict, output_path: str):
    if not estrutura:
        print("⚠️ Nenhuma questão a salvar.")
        return

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(estrutura, f, indent=2, ensure_ascii=False)
    print(f"✅ questions.json salvo em: {output_path}")

def main():
    print("🚀 Iniciando pipeline principal...\n")
    
    estrutura = run_all_pdfs.main()

    if not estrutura:
        print("❌ Nenhuma estrutura gerada.")
        return

    # Aqui podemos incluir validações futuras, se necessário
    output_file = os.path.join(os.path.dirname(__file__), "..", "questions.json")
    salvar_questions_json(estrutura, output_file)

if __name__ == "__main__":
    main()