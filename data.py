# Database setup
import sqlite3

DB_NAME = 'bookmarks.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookmarks
                 (id INTEGER PRIMARY KEY, url TEXT, title TEXT, description TEXT, tags TEXT)''')

    conn.commit()
    conn.close()


# Save bookmark
def save_bookmark(url, title=None, description=None, tags=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''INSERT INTO bookmarks (url, title, description, tags)
                    VALUES (?, ?, ?, ?)''', (url, title, description, tags))
    conn.commit()
    conn.close()


# Save bookmark
def delete_bookmark_by_id(id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('delete from bookmarks where id= ?', (id,))
    conn.commit()
    conn.close()

# List bookmarks
def list_bookmarks():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM bookmarks")
    bookmarks = c.fetchall()
    conn.close()
    return bookmarks
