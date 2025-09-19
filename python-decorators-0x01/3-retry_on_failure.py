import time
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

def retry_on_failure(retries=3, delay=2):
    """
    Decorator that retries a function a specified number of times with a delay
    if it raises an exception.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Attempt {i + 1} failed: {e}")
                    if i < retries - 1:
                        print(f"Retrying in {delay} seconds...")
                        time.sleep(delay)
                    else:
                        print("All retry attempts failed. Raising the original exception.")
                        raise
        return wrapper
    return decorator

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
    cursor.execute("INSERT OR IGNORE INTO users (id, name) VALUES (?, ?)", (1, 'Alice'))
    cursor.execute("INSERT OR IGNORE INTO users (id, name) VALUES (?, ?)", (2, 'Bob'))
    conn.commit()
    conn.close()

# Set up the database
setup_database()

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    # This function is intentionally designed to fail on the first call for demonstration.
    # A real-world scenario might involve a network issue or a temporary database lock.
    global attempts
    attempts += 1
    if attempts < 2:
        raise sqlite3.OperationalError("Simulated database lock or temporary failure.")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

# Global counter to track attempts for the simulation
attempts = 0

# Attempt to fetch users with automatic retry on failure
users = fetch_users_with_retry()
print(f"Users fetched successfully: {users}")