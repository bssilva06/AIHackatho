def parse_book_entries(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    collections = []
    current_collection = {}
    current_books = []
    reading_books = False

    for line in lines:
        line = line.strip()

        if line.startswith("Collection:"):
            if current_collection:
                current_collection["books"] = current_books
                collections.append(current_collection)
                current_books = []

            current_collection = {"collection": line.replace("Collection:", "").strip()}
        
        elif line.startswith("Grade:"):
            current_collection["grade"] = line.replace("Grade:", "").strip()
        
        elif line.startswith("Description:"):
            current_collection["description"] = line.replace("Description:", "").strip()
        
        elif line == "Book Titles:":
            reading_books = True
        
        elif reading_books:
            if line.startswith("- "):
                current_books.append(line[2:].strip())
            elif line == "---":
                reading_books = False

    # Add last collection
    if current_collection:
        current_collection["books"] = current_books
        collections.append(current_collection)

    return collections