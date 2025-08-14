import os
import re
import json
import openai
#
from extract_clean_text import extract_clean_text

# Configuração da API
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def _build_system_prompt():
    return (
        "Você é um gerador de questões objetivas de altíssima qualidade.\n"
        "Regras obrigatórias:\n"
        "1) Produza EXATAMENTE um array JSON (sem texto fora do array).\n"
        "2) Cada item: {\"question\": str, \"options\": [str,str,str,str], \"answer\": 0|1|2|3}.\n"
        "3) UMA única correta por item; as erradas devem ser plausíveis e distintas.\n"
        "4) Não copie frases literais do texto; reformule com clareza técnica.\n"
        "5) Evite questões duplicadas ou muito semelhantes.\n"
        "6) Linguagem objetiva, nível de bancas (PF, PRF, CESPE, FCC), sem ambiguidade.\n"
        "7) Sem comentários, sem justificativas, sem vírgula final ou chaves extras.\n"
        "8) Use exclusivamente informações do [TEXTO]. Se faltar base, reformule para interpretação/estrutura do texto.\n"
        "9) Se não houver material suficiente, foque em inferência e interpretação do que existe, nunca em conteúdo externo."
    )

def _few_shot_example():
    return [
        {
            "role": "user",
            "content": (
                "[INSTRUÇÃO] Gere 2 questões no formato especificado.\n"
                "[TEXTO] A 'Navegação de Cabotagem' refere-se ao transporte marítimo entre portos de um mesmo país, "
                "diferente da navegação de longo curso, que conecta portos de países distintos."
            )
        },
        {
            "role": "assistant",
            "content": json.dumps([
                {
                    "question": "Qual característica distingue a navegação de cabotagem da de longo curso?",
                    "options": [
                        "A cabotagem opera entre portos do mesmo país.",
                        "A cabotagem utiliza apenas navios de pequeno porte.",
                        "A cabotagem exige travessia oceânica obrigatória.",
                        "A cabotagem é exclusiva para cargas perigosas."
                    ],
                    "answer": 0
                },
                {
                    "question": "Em qual situação a navegação de longo curso é a alternativa adequada?",
                    "options": [
                        "Carga entre dois portos do mesmo litoral.",
                        "Transporte entre portos de países diferentes.",
                        "Distribuição entre cidades ribeirinhas.",
                        "Transporte interno em lagos navegáveis."
                    ],
                    "answer": 1
                }
            ], ensure_ascii=False)
        }
    ]

def gerar_questoes(texto: str, qtd: int = 40) -> str:
    system_prompt = _build_system_prompt()
    user_prompt = (
        f"[INSTRUÇÃO] Com base no conteúdo abaixo, gere {qtd} questões objetivas (4 alternativas) "
    f"em um ÚNICO array JSON minificado de {qtd} objetos. NÃO escreva nada antes ou depois do array e  compacte a redação ".\n"
    f"[FORMATO] [{'{'!s}\"question\":\"...\",\"options\":[\"...\",\"...\",\"...\",\"...\"],\"answer\":0..3{'}'!s}] x{qtd}\n"
    f"[TEXTO]\n{texto}"
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages += _few_shot_example()
    messages.append({"role": "user", "content": user_prompt})

    resp = client.chat.completions.create(
        model="gpt-5-nano",
        messages=messages
    )

    raw = resp.choices[0].message.content
    # tenta extrair o array JSON
    m = re.search(r"\[.*\]\s*\Z", raw.strip(), flags=re.S)
    if m:
        return m.group(0)
    return raw.strip()

def salvar_questoes_em_json(questoes_json: str, output_path: str):
    try:
        data = json.loads(questoes_json)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Questões salvas em {output_path}")
    except Exception as e:
        print("❌ Erro ao salvar JSON:", e)

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Uso: python generate_from_pdf.py <arquivo.pdf> <saida.json>")
        exit(1)

    pdf_path = sys.argv[1]
    output_json = sys.argv[2]

    print("🔍 Extraindo texto do PDF...")
    texto_completo = extract_clean_text(pdf_path)

    #print(texto_completo)
    #print(erro)

    print("🤖 Enviando para o OpenAI...")
    resposta = gerar_questoes(texto_completo, qtd=40)
    print(resposta)

    print("💾 Salvando questões...")
    salvar_questoes_em_json(resposta, output_json)