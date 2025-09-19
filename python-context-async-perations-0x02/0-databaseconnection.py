import sqlite3

class DatabaseConnection:
    """
    A custom class-based context manager for handling SQLite database connections.
    """
    def __init__(self, db_name):
        """
        Initializes the context manager with the database name.
        """
        self.db_name = db_name
        self.conn = None

    def __enter__(self):
        """
        Establishes a connection to the database and returns the connection object.
        This method is called when the 'with' statement is entered.
        """
        self.conn = sqlite3.connect(self.db_name)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Closes the database connection. This method is called when the 'with' 
        statement is exited, even if an exception occurs.
        """
        if self.conn:
            self.conn.close()
            print("Database connection closed.")
        # Returning None (or a Falsey value) allows any exception to propagate.

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
            email TEXT
        )
    ''')
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (?, ?, ?)", (1, 'Alice', 'alice@example.com'))
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (?, ?, ?)", (2, 'Bob', 'bob@example.com'))
    conn.commit()
    conn.close()
    print("Database setup complete.")

# --- Main execution block ---
if __name__ == "__main__":
    setup_database()

    # Use the context manager with the 'with' statement
    try:
        with DatabaseConnection('users.db') as conn:
            print("\nDatabase connection opened.")
            cursor = conn.cursor()
            
            # Perform the query
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
            
            # Print the results
            print("Query results:")
            for row in results:
                print(row)
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
