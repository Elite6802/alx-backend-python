#!/usr/bin/python3
import mysql.connector

def stream_users_in_batches(batch_size):
    """Generator that fetches users in batches from the database"""
    conn = mysql.connector.connect(
        host="localhost",
        user="root",       # change if needed
        password="",       # change if needed
        database="ALX_prodev"
    )
    cursor = conn.cursor(dictionary=True)
    offset = 0

    while True:
        cursor.execute(
            "SELECT * FROM user_data LIMIT %s OFFSET %s",
            (batch_size, offset)
        )
        batch = cursor.fetchall()
        if not batch:
            break
        for row in batch:
            yield row
        offset += batch_size

    cursor.close()
    conn.close()

def batch_processing(batch_size):
    """Processes batches to filter users over age 25"""
    batch_gen = stream_users_in_batches(batch_size)
    # Single loop to iterate over generator
    for user in batch_gen:
        if user['age'] > 25:
            print(user)
