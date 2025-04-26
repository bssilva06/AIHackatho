import sqlite3
from datetime import datetime

conn = sqlite3.connect('search_history.db', check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS searches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grade TEXT,
    subject TEXT,
    theme TEXT,
    timestamp TEXT
)
''')
conn.commit()

def save_search(grade, subject, theme):
    timestamp = datetime.now().isoformat()
    c.execute("INSERT INTO searches (grade, subject, theme, timestamp) VALUES (?, ?, ?, ?)",
              (grade, subject, theme, timestamp))
    conn.commit()
