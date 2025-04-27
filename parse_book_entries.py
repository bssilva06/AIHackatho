def parse_book_entries(file_path):
    """
    Returns a list like:
    [
        {
            "collection": "Culturally Responsive Collections — Multicultural Edition",
            "grades": {
                "PreK":         "$275.00",
                "Kindergarten": "$275.00",
                "Grade 1":      "$275.00",
                ...
            }
        },
        {
            "collection": "Optimistic Library",
            "grades": {
                "Kindergarten": "$250.00",
                "Grade 1":      "$270.00",
                "Grade 2":      "$270.00",
                ...
            }
        },
        ...
    ]
    """
    collections = {}          # key = collection name, value = {"collection": name, "grades": {}}

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    current_name   = None     # collection name we’re inside
    current_grade  = None     # last "Grade:" seen

    for raw in lines:
        line = raw.strip()

        # ---------- new collection block ----------
        if line.startswith("Collection:"):
            current_name = line.replace("Collection:", "").strip()
            # create the entry if we haven’t seen this collection before
            if current_name not in collections:
                collections[current_name] = {
                    "collection": current_name,
                    "grades": {}
                }
            current_grade = None

        # ---------- grade ----------
        elif line.startswith("Grade:"):
            current_grade = line.replace("Grade:", "").strip()

        # ---------- price ----------
        elif line.startswith("Your Price:") and current_name and current_grade:
            price = line.replace("Your Price:", "").strip()
            collections[current_name]["grades"][current_grade] = price
            current_grade = None   # reset until we see next Grade:

        # (you can keep descriptions/books if you ever need them)

    # convert dict → list for easy iteration
    return list(collections.values())