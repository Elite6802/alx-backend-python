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

def transactional(func):
    """
    Decorator that manages database transactions, automatically committing
    on success or rolling back on error.
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            print(f"Transaction failed, rolling back changes: {e}")
            conn.rollback()
            raise
    return wrapper

# Create a dummy database for the example
def setup_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT
        )
    ''')
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (?, ?, ?)", (1, 'Alice', 'alice@example.com'))
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (?, ?, ?)", (2, 'Bob', 'bob@example.com'))
    conn.commit()
    conn.close()

# Set up the database
setup_database()

@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))

# Update user's email with automatic transaction handling
try:
    update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')
    print("User email updated successfully.")

    # Verify the update
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = 1")
    user = cursor.fetchone()
    print(f"Updated user data: {user}")
    conn.close()

except Exception as e:
    print(f"An error occurred: {e}")