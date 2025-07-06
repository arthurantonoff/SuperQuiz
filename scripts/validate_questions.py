from typing import List, Dict
import hashlib

def is_valid_question(q: Dict) -> bool:
    """
    Valida se a questão possui estrutura básica correta:
    - Contém os campos esperados
    - 4 alternativas válidas e distintas
    - Índice da resposta correto
    """
    if not q or "question" not in q or "options" not in q or "answer" not in q:
        return False

    if not isinstance(q["question"], str) or not q["question"].strip():
        return False

    if not isinstance(q["options"], list) or len(q["options"]) != 4:
        return False

    if not all(isinstance(opt, str) and opt.strip() for opt in q["options"]):
        return False

    if len(set(q["options"])) < 4:
        return False

    if not isinstance(q["answer"], int) or not (0 <= q["answer"] < 4):
        return False

    return True

def remove_duplicates(questions: List[Dict]) -> List[Dict]:
    """
    Remove questões duplicadas com base no hash da pergunta e alternativas.
    """
    seen = set()
    result = []

    for q in questions:
        if not is_valid_question(q):
            continue

        hash_base = q["question"].strip() + "||" + "||".join([opt.strip() for opt in q["options"]])
        hash_q = hashlib.md5(hash_base.encode("utf-8")).hexdigest()

        if hash_q not in seen:
            seen.add(hash_q)
            result.append(q)

    return result