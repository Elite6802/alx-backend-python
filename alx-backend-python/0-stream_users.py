#!/usr/bin/python3
import mysql.connector

def stream_users():
    """Generator that yields rows one by one from user_data table"""
    # Connect to the ALX_prodev database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",       # change if needed
        password="",       # change if needed
        database="ALX_prodev"
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data")

    # Yield each row one by one (single loop)
    for row in cursor:
        yield row

    # Cleanup
    cursor.close()
    conn.close()
