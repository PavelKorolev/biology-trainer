import re

INPUT_FILE = "biotest.txt"

OPTION_H_RE = re.compile(r"^h\)", re.IGNORECASE)
PAGE_RE = re.compile(r"^\d+$")
QUESTION_RE = re.compile(r"^\d+\.")

def find_page_numbers(lines):

    pages = []
    errors = []

    for i in range(len(lines) - 2):

        line1 = lines[i].strip()
        line2 = lines[i+1].strip()
        line3 = lines[i+2].strip()

        if OPTION_H_RE.match(line1):

            if PAGE_RE.match(line2):

                if QUESTION_RE.match(line3):

                    pages.append((i+1, int(line2)))

                else:
                    errors.append((i+1, "ПОСЛЕ НОМЕРА СТРАНИЦЫ НЕТ ВОПРОСА"))

            else:
                errors.append((i+1, "ПОСЛЕ h) НЕТ НОМЕРА СТРАНИЦЫ"))

    return pages, errors


if __name__ == "__main__":

    with open(INPUT_FILE, encoding="utf-8") as f:
        lines = f.readlines()

    pages, errors = find_page_numbers(lines)

    print("Найдено номеров страниц:", len(pages))
    print("Ожидалось:", 234)

    if len(pages) != 234:
        print("❌ НЕСОВПАДЕНИЕ КОЛИЧЕСТВА")

    print("\nОшибки структуры:", len(errors))

    for e in errors[:20]:
        print(e)
