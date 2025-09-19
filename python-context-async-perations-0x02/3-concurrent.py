import asyncio
import aiosqlite

async def setup_database():
    """
    Sets up a dummy SQLite database with a 'users' table for demonstration.
    This is a synchronous function and is not part of the concurrent fetching.
    """
    async with aiosqlite.connect('users.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER
            )
        ''')
        await db.execute("INSERT OR IGNORE INTO users (id, name, age) VALUES (?, ?, ?)", (1, 'Alice', 30))
        await db.execute("INSERT OR IGNORE INTO users (id, name, age) VALUES (?, ?, ?)", (2, 'Bob', 22))
        await db.execute("INSERT OR IGNORE INTO users (id, name, age) VALUES (?, ?, ?)", (3, 'Charlie', 45))
        await db.execute("INSERT OR IGNORE INTO users (id, name, age) VALUES (?, ?, ?)", (4, 'David', 55))
        await db.commit()
    print("Database setup complete.")


async def async_fetch_users():
    """
    Asynchronously fetches all users from the database.
    """
    print("Fetching all users...")
    async with aiosqlite.connect('users.db') as db:
        cursor = await db.execute("SELECT * FROM users")
        users = await cursor.fetchall()
        await cursor.close()
    return users


async def async_fetch_older_users():
    """
    Asynchronously fetches users older than 40 from the database.
    """
    print("Fetching users older than 40...")
    async with aiosqlite.connect('users.db') as db:
        cursor = await db.execute("SELECT * FROM users WHERE age > ?", (40,))
        older_users = await cursor.fetchall()
        await cursor.close()
    return older_users


async def fetch_concurrently():
    """
    Runs multiple database queries concurrently using asyncio.gather().
    """
    # Create the database first to ensure it's ready
    await setup_database()

    # Schedule both asynchronous functions to run concurrently
    results = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )

    all_users, older_users = results

    print("\n--- Concurrently Fetched Results ---")
    print("All users:")
    for user in all_users:
        print(f"  - {user}")
    
    print("\nUsers older than 40:")
    for user in older_users:
        print(f"  - {user}")


# Entry point to run the asynchronous main function
if __name__ == "__main__":
    asyncio.run(fetch_concurrently())
