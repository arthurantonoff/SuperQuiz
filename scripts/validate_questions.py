import random

def rotate_options(options: list) -> (list, int):
    """Gira a lista de opções aleatoriamente e retorna o novo índice da resposta correta."""
    n = random.randint(0, 3)
    rotated = options[n:] + options[:n]
    correct_index = (0 - n) % 4
    return rotated, correct_index

def validar_estrutura(estrutura: dict) -> dict:
    """
    Valida e ajusta a estrutura geral de questões no formato:
    { "tema": { "subtema": [ {question, options, answer}, ... ] } }

    - Remove entradas inválidas
    - Garante campos obrigatórios
    - Reorganiza opções e atualiza índice da resposta correta
    """
    estrutura_corrigida = {}

    for tema, subtemas in estrutura.items():
        estrutura_corrigida[tema] = {}

        for subtema, questoes in subtemas.items():
            lista_valida = []

            for q in questoes:
                if not isinstance(q, dict):
                    continue
                if not all(k in q for k in ("question", "options", "answer")):
                    continue
                if not isinstance(q["options"], list) or len(q["options"]) != 4:
                    continue
                if not isinstance(q["answer"], int) or not (0 <= q["answer"] < 4):
                    continue

                # Embaralhar opções
                correta = q["options"][q["answer"]]
                restantes = [opt for i, opt in enumerate(q["options"]) if i != q["answer"]]
                novas_opcoes, nova_resposta = rotate_options([correta] + restantes)

                item = {
                    "question": q["question"].strip(),
                    "options": novas_opcoes,
                    "answer": nova_resposta
                }
                lista_valida.append(item)

            estrutura_corrigida[tema][subtema] = lista_valida

    return estrutura_corrigida