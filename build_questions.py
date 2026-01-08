import json
import re

# ================= НАСТРОЙКИ =================

INPUT_FILE = "biologyV3.txt"      # ТЕКСТ с вопросами + ключами
OUTPUT_FILE = "questions_all.json"

MIN_Q = 1
MAX_Q = 1000

# ============================================


def parse_questions(text: str):
    questions = {}

    lines = [line.rstrip() for line in text.splitlines()]
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # начало вопроса: "251."
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

        # собираем текст вопроса (может быть несколько строк)
        while i < len(lines) and not re.match(r"^[a-hA-H]\)", lines[i].strip()):
            if lines[i].strip():
                question_parts.append(lines[i].strip())
            i += 1

        question_text = " ".join(question_parts).strip()

        # варианты ответа
        options = {}
        while i < len(lines):
            opt_line = lines[i]

            # OCR-косяки
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

    # пример: 251 SNSNNSN
    pattern = re.compile(r"\b(\d{1,4})\s+([SN]{4,8})\b")

    for num, mask in pattern.findall(text):
        num = int(num)
        if num < MIN_Q or num > MAX_Q:
            continue

        correct = []
        for i, ch in enumerate(mask):
            if ch == "S":
                correct.append(chr(ord("A") + i))

        answers[num] = correct

    return answers


def main():
    # ✅ ЧИТАЕМ ИСХОДНЫЙ TXT
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

    print(f"\nДиагностика диапазона {MIN_Q}–{MAX_Q}:\n")

    print("❌ Нет вопроса, но есть ответ:")
    print(sorted(a_nums - q_nums))

    print("\n❌ Есть вопрос, но нет ответа:")
    print(sorted(q_nums - a_nums))

    print("\n❌ Нет ни вопроса, ни ответа:")
    print(sorted(all_nums - (q_nums | a_nums)))
    # ---------------------

    # ✅ ПИШЕМ JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nГотово: сохранено {len(result)} вопросов ({MIN_Q}–{MAX_Q}) в {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
