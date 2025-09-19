import sqlite3

class ExecuteQuery:
    """
    A custom class-based context manager that executes a given SQL query
    and manages the database connection and cursor.
    """
    def __init__(self, db_name, query, params=None):
        """
        Initializes the context manager with the database name, query, and parameters.
        """
        self.db_name = db_name
        self.query = query
        self.params = params
        self.conn = None
        self.cursor = None

    def __enter__(self):
        """
        Establishes a database connection, creates a cursor, executes the query,
        and returns the cursor object.
        """
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        print(f"Executing query: {self.query}")
        if self.params:
            self.cursor.execute(self.query, self.params)
        else:
            self.cursor.execute(self.query)
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Closes the cursor and the database connection, handling any potential exceptions.
        """
        if exc_type is None:
            # Commit the transaction if no exception occurred
            self.conn.commit()
        else:
            # Rollback the transaction on an error
            self.conn.rollback()
            print(f"An exception of type {exc_type.__name__} occurred during query execution.")
            
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            print("Database connection closed.")
        # Returning False (or None) allows the exception to propagate.
        return False

# --- Helper function to set up the database for the example ---
def setup_database():
    """
    Creates a dummy database with a users table for demonstration.
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER,
            email TEXT
        )
    ''')
    cursor.execute("INSERT OR IGNORE INTO users (id, name, age, email) VALUES (?, ?, ?, ?)", (1, 'Alice', 30, 'alice@example.com'))
    cursor.execute("INSERT OR IGNORE INTO users (id, name, age, email) VALUES (?, ?, ?, ?)", (2, 'Bob', 22, 'bob@example.com'))
    cursor.execute("INSERT OR IGNORE INTO users (id, name, age, email) VALUES (?, ?, ?, ?)", (3, 'Charlie', 45, 'charlie@example.com'))
    conn.commit()
    conn.close()
    print("Database setup complete.")

# --- Main execution block ---
if __name__ == "__main__":
    setup_database()

    # Use the context manager with the 'with' statement
    try:
        query_string = "SELECT * FROM users WHERE age > ?"
        query_param = (25,) # Note the comma to make it a tuple with one element

        with ExecuteQuery('users.db', query_string, query_param) as cursor:
            # Fetch the results from the executed query
            results = cursor.fetchall()
            
            # Print the results
            print("\nQuery results:")
            if results:
                for row in results:
                    print(row)
            else:
                print("No users found matching the criteria.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
