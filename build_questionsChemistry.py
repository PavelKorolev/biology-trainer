import json
import re

# ================= НАСТРОЙКИ =================

INPUT_FILE = "chemistryV2.txt"
OUTPUT_FILE = "questions_allChemistry.json"

MIN_Q = 1
MAX_Q = 126

# ============================================


def parse_questions(text: str):
    questions = {}

    lines = [line.rstrip() for line in text.splitlines()]
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # ⛔ стоп: начался ключ ответов
        if "Kľúč k otázkam" in line:
            break

        # начало вопроса: "19."
        m = re.match(r"^(\d+)\.\s*(.*)", line)
        if not m:
            i += 1
            continue

        num = int(m.group(1))
        if num < MIN_Q or num > MAX_Q:
            i += 1
            continue

        question_parts = [m.group(2).strip()]
        i += 1

        # собираем текст вопроса
        while i < len(lines) and not re.match(r"^[a-hA-H]\)", lines[i].strip()):
            if lines[i].strip():
                question_parts.append(lines[i].strip())
            i += 1

        question_text = " ".join(question_parts).strip()

        # варианты ответа
        options = {}
        while i < len(lines):
            opt_line = lines[i]

            opt_line = opt_line.replace("ť)", "g)")
            opt_line = opt_line.replace("Ť)", "G)")
            opt_line = opt_line.replace("\u00A0", " ").strip()

            m_opt = re.match(r"^([a-hA-H])\)\s*(.+)", opt_line)
            if not m_opt:
                break

            options[m_opt.group(1).upper()] = m_opt.group(2).strip()
            i += 1

        questions[num] = {
            "id": num,
            "question": question_text,
            "options": options,
            "correct": []
        }

    return questions



def parse_answers(text: str):
    answers = {}

    lines = text.splitlines()

    for line in lines:
        line = line.strip()

        # формат ключа химии: "19. NSNNNSSS"
        m = re.match(r"^(\d{1,4})\.\s*([SN]{4,8})$", line)
        if not m:
            continue

        num = int(m.group(1))
        if num < MIN_Q or num > MAX_Q:
            continue

        mask = m.group(2)

        correct = []
        for i, ch in enumerate(mask):
            if ch == "S":
                correct.append(chr(ord("A") + i))

        answers[num] = correct

    return answers


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    questions = parse_questions(text)
    answers = parse_answers(text)

    result = []
    for num in range(MIN_Q, MAX_Q + 1):
        if num in questions and num in answers:
            q = questions[num]
            q["correct"] = answers[num]
            result.append(q)

    # ---- диагностика ----
    all_nums = set(range(MIN_Q, MAX_Q + 1))
    q_nums = set(questions.keys())
    a_nums = set(answers.keys())

    print(f"\nДиагностика химии ({MIN_Q}–{MAX_Q}):\n")

    print("❌ Нет вопроса, но есть ответ:")
    print(sorted(a_nums - q_nums))

    print("\n❌ Есть вопрос, но нет ответа:")
    print(sorted(q_nums - a_nums))

    print("\n❌ Нет ни вопроса, ни ответа:")
    print(sorted(all_nums - (q_nums | a_nums)))
    # ---------------------

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nГотово: сохранено {len(result)} вопросов по химии → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
