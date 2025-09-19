import time
import sqlite3
import functools

# Global cache dictionary
query_cache = {}

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

def cache_query(func):
    """
    Decorator that caches the results of a database query based on the query string.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the query from the arguments. Assuming the query is a keyword argument 'query'.
        # This can be made more robust to handle positional arguments as well.
        query = kwargs.get('query') or args[1] if len(args) > 1 else None

        if query in query_cache:
            print(f"Using cached result for query: {query}")
            return query_cache[query]
        else:
            print(f"Executing and caching result for query: {query}")
            result = func(*args, **kwargs)
            query_cache[query] = result
            return result
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
    cursor.execute("INSERT OR IGNORE INTO users (id, name) VALUES (?, ?)", (1, 'Alice'))
    cursor.execute("INSERT OR IGNORE INTO users (id, name) VALUES (?, ?)", (2, 'Bob'))
    conn.commit()
    conn.close()

# Set up the database
setup_database()

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    time.sleep(1)  # Simulate a slow query
    return cursor.fetchall()

#### First call will cache the result
print("--- First Call ---")
users = fetch_users_with_cache(query="SELECT * FROM users")
print(f"Users fetched: {users}")

#### Second call will use the cached result
print("\n--- Second Call ---")
users_again = fetch_users_with_cache(query="SELECT * FROM users")
print(f"Users fetched again: {users_again}")