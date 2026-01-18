import re

INPUT_FILE = "biologyV3.txt"
EXPECTED = list("ABCDEFGH")

def find_bad_questions(text):
    lines = text.splitlines()
    i = 0
    bad = []

    while i < len(lines):
        m = re.match(r"^(\d+)\.", lines[i].strip())
        if not m:
            i += 1
            continue

        qnum = int(m.group(1))
        i += 1

        option_lines = []

        while i < len(lines) and not re.match(r"^\d+\.", lines[i]):
            line = lines[i]
            # если строка содержит хотя бы один вариант
            if re.search(r"\b[a-h]\)", line, re.IGNORECASE):
                option_lines.append(line)
            i += 1

        # 1️⃣ проверка: ровно 8 строк с вариантами
        if len(option_lines) != 8:
            bad.append((qnum, "НЕ 8 строк вариантов", option_lines))
            continue

        # 2️⃣ проверка: в каждой строке ТОЛЬКО один вариант
        for line in option_lines:
            found = re.findall(r"\b([a-h])\)", line, re.IGNORECASE)
            if len(found) != 1:
                bad.append((qnum, "СКЛЕЕНЫ ВАРИАНТЫ", option_lines))
                break

        # 3️⃣ проверка порядка
        letters = [
            re.search(r"\b([a-h])\)", l, re.IGNORECASE).group(1).upper()
            for l in option_lines
            if re.search(r"\b([a-h])\)", l, re.IGNORECASE)
        ]

        if letters != EXPECTED:
            bad.append((qnum, "НЕВЕРНЫЙ ПОРЯДОК", option_lines))

    return bad


if __name__ == "__main__":
    with open(INPUT_FILE, encoding="utf-8") as f:
        text = f.read()

    bad = find_bad_questions(text)

    print(f"\nНайдено битых вопросов: {len(bad)}\n")

    for qnum, reason, lines in bad:
        print(f"❌ Вопрос {qnum}: {reason}")