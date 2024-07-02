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

def search_by_url_pattern(url):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    query="SELECT * FROM bookmarks WHERE url LIKE ?"
    c.execute(query,(url,))

    bookmarks = c.fetchall()
    conn.close()
    return bookmarks

def search_by_exact_url(url):
    conn = sqlite3.connect(DB_NAME)
    print(f'{url}xxxxxxxx')
    c = conn.cursor()
    query="SELECT * FROM bookmarks WHERE url=?"
    c.execute(query,(url,))
    bookmarks = c.fetchall()
    conn.close()
    print(bookmarks)
    return bookmarks

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
