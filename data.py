# Database setup
import sqlite3
from linkeeper import logger

DB_NAME = 'bookmarks.db'
def init_db():
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS bookmarks
                     (id INTEGER PRIMARY KEY, url TEXT, title TEXT, description TEXT, tags TEXT)''')

        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Failed to initialize database: {e}")
    finally:
        conn.close()

def search_by_url_pattern(url, tags):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        params = [f'%{url}%',f'%{url}%', f'%{url}%']
        i=0
        tag_query = ' or (' if len(tags)>0 else ''
        for tag in tags:
            if i>0: tag_query += ' or  '
            tag_query += f" tags like ? " 
            params.append(f'%{tag}%')
        tag_query += " )" if len(tags)>0 else ''

        query = "SELECT * FROM bookmarks WHERE url LIKE ? or title LIKE ? or description LIKE ? " + tag_query
        logger.info(f"Query: {query}, Params: {params}")
        c.execute(query, params)

        bookmarks = c.fetchall()
        return bookmarks
    except sqlite3.Error as e:
        logger.error(f"Failed to search bookmarks by URL pattern: {e}")
        return []

def search_by_exact_url(url):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        query = "SELECT * FROM bookmarks WHERE url=?"
        c.execute(query, (url,))
        bookmarks = c.fetchall()
        return bookmarks
    except sqlite3.Error as e:
        logger.error(f"Failed to search bookmarks by exact URL: {e}")
        return []

def delete_bookmark_by_id(id):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('DELETE FROM bookmarks WHERE id= ?', (id,))
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Failed to delete bookmark: {e}")
    finally:
        conn.close()

def list_bookmarks():
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM bookmarks")
        bookmarks = c.fetchall()
        return bookmarks
    except sqlite3.Error as e:
        logger.error(f"Failed to retrieve bookmarks: {e}")
        return []

# Save bookmark
def save_bookmark(url, title=None, description=None, tags=None):
    conn = sqlite3.connect(DB_NAME)
    try :
        c = conn.cursor()
        c.execute('''INSERT INTO bookmarks (url, title, description, tags)
                        VALUES (?, ?, ?, ?)''', (url, title, description, tags))
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Failed to save bookmark: {e}")
    finally:
        conn.close()

