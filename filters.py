import re

def normalize_grade(grade_text):
    grade_text = grade_text.lower().strip()

    if "kindergarten" in grade_text or grade_text.startswith("k"):
        return 0

    match = re.search(r'(\d+)', grade_text)
    if match:
        return int(match.group(1))

    return None

def grade_in_page(user_grade_text, page_text):
    user_grade = normalize_grade(user_grade_text)

    if user_grade is None:
        return False

    matches = re.findall(r'Grades?\s*(\d+)[–-](\d+)', page_text, flags=re.IGNORECASE)
    single_matches = re.findall(r'Grade\s*(\d+)', page_text, flags=re.IGNORECASE)

    if matches:
        for start, end in matches:
            if int(start) <= user_grade <= int(end):
                return True

    if single_matches:
        for grade in single_matches:
            if int(grade) == user_grade:
                return True

    return False
