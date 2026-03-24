import json
import sys

files = sys.argv[1:] if len(sys.argv) > 1 else [
    "questions_all.json",
    "questions_allChemistry.json",
]

for path in files:
    with open(path, encoding="utf-8") as f:
        questions = json.load(f)

    problems = []
    for q in questions:
        n_options = len(q["options"])
        if q["correct"]:
            max_correct_pos = max(ord(c) - ord("A") + 1 for c in q["correct"])
            if max_correct_pos > n_options:
                problems.append((q["id"], n_options, max_correct_pos))

    print(f"{path}: битых вопросов: {len(problems)}")
    for qid, opts, mask in problems:
        print(f"  Q{qid}: вариантов {opts}, но правильный ответ на позиции {mask}")
