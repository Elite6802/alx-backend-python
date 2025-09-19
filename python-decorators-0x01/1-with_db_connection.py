import sqlite3
import functools

def with_db_connection(func):
    """
    Decorator that opens a database connection, passes it to the decorated function,
    and ensures the connection is closed afterward.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            result = func(conn, *args, **kwargs)
            return result
        finally:
            conn.close()
    return wrapper

# Create a dummy database for the example
def setup_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    ''')
    cursor.execute("INSERT INTO users (name) VALUES (?)", ('Alice',))
    cursor.execute("INSERT INTO users (name) VALUES (?)", ('Bob',))
    conn.commit()
    conn.close()

# Set up the database
setup_database()

@with_db_connection
def get_user_by_id(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

# Fetch user by ID with automatic connection handling
user = get_user_by_id(user_id=1)
print(user)