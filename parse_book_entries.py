def parse_book_entries(file_path):
    collections = {}

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    current_name = None
    current_grade = None

    for raw in lines:
        line = raw.strip()

        if line.startswith("Collection:"):
            current_name = line.replace("Collection:", "").strip()
            if current_name not in collections:
                collections[current_name] = {"collection": current_name, "grades": {}}
            current_grade = None

        elif line.startswith("Grade:"):
            current_grade = line.replace("Grade:", "").strip()

        elif line.startswith("Your Price:") and current_name and current_grade:
            price = line.replace("Your Price:", "").strip()
            collections[current_name]["grades"][current_grade] = price
            current_grade = None

    return list(collections.values())