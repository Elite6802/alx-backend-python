import mysql.connector
import csv
import uuid
import requests
from io import StringIO

# --- Database Connection ---
def connect_db():
    """Connect to MySQL server"""
    return mysql.connector.connect(
        host="localhost",
        user="root",       # change if needed
        password=""        # change if needed
    )

def create_database(connection):
    """Create ALX_prodev database if it doesn't exist"""
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
    connection.commit()

def connect_to_prodev():
    """Connect to ALX_prodev database"""
    return mysql.connector.connect(
        host="localhost",
        user="root",       # change if needed
        password="",       # change if needed
        database="ALX_prodev"
    )

def create_table(connection):
    """Create user_data table if it doesn't exist"""
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_data (
            user_id CHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL(5,2) NOT NULL
        )
    """)
    connection.commit()

def insert_data(connection, data):
    """Insert data into user_data table"""
    cursor = connection.cursor()
    for row in data:
        user_id = str(uuid.uuid4())
        name, email, age = row
        cursor.execute("""
            INSERT INTO user_data (user_id, name, email, age)
            VALUES (%s, %s, %s, %s)
        """, (user_id, name, email, age))
    connection.commit()

# --- Generator Function ---
def stream_rows(connection):
    """Generator that yields rows one by one from user_data"""
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data")
    for row in cursor:
        yield row

# --- Main Execution ---
if __name__ == "__main__":
    # Connect to MySQL server and create database
    conn = connect_db()
    create_database(conn)
    conn.close()

    # Connect to ALX_prodev and create table
    conn = connect_to_prodev()
    create_table(conn)

    # Download CSV data
    url = "https://s3.amazonaws.com/alx-intranet.hbtn.io/uploads/misc/2024/12/3888260f107e3701e3cd81af49ef997cf70b6395.csv?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIARDDGGGOUSBVO6H7D%2F20250906%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20250906T071533Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&X-Amz-Signature=b8db9d9e516a966b6771a8ea4b0ac99125262abad119a8dbd70e7bfbfa8aea83"
    response = requests.get(url)
    response.raise_for_status()
    csv_file = StringIO(response.text)
    reader = csv.reader(csv_file)
    next(reader)  # skip header
    insert_data(conn, reader)

    # Stream rows using generator
    print("Streaming rows from user_data:")
    for row in stream_rows(conn):
        print(row)

    conn.close()
