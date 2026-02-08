"""
Database helper functions for realpage_user table
Simple CRUD operations for managing users.
"""

import sqlite3
from pathlib import Path


def get_db_path():
    """Get the path to realpage.db"""
    script_dir = Path(__file__).parent
    return script_dir.parent / "databases" / "realpage.db"


def last_row_db():
    """
    Get the next available user ID.

    Returns:
        int: Next user ID (e.g., 1, 2, 3...)
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(id) FROM realpage_user")
    result = cursor.fetchone()
    conn.close()

    if result[0]:
        return result[0] + 1
    return 1


def retrieve_user(user_id):
    """
    Retrieve a user by their ID.

    Args:
        user_id (int): User ID to retrieve

    Returns:
        dict: User data with all columns, or None if not found
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM realpage_user WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def retrieve_user_by_email(email):
    """
    Retrieve a user by their email.

    Args:
        email (str): User email

    Returns:
        dict: User data with all columns, or None if not found
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM realpage_user WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def insert_user(**kwargs):
    """
    Insert a new user into the database.

    Args:
        **kwargs: Column names and values

    Returns:
        int: New user ID if successful, None if error

    Example:
        insert_user(
            username='John Doe',
            email='john@realpage.com',
            password_hash='$2b$12$...',
            role='realpage_user'
        )
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        columns = ", ".join(kwargs.keys())
        placeholders = ", ".join(["?" for _ in kwargs])
        values = list(kwargs.values())

        query = f"INSERT INTO realpage_user ({columns}) VALUES ({placeholders})"
        cursor.execute(query, values)
        conn.commit()

        new_id = cursor.lastrowid
        conn.close()

        print(f"✓ Inserted user with ID: {new_id}")
        return new_id

    except Exception as e:
        conn.close()
        print(f"Error inserting user: {e}")
        return None


def update_user(user_id, **kwargs):
    """
    Update a user by their ID.

    Args:
        user_id (int): User ID to update
        **kwargs: Column names and values to update

    Returns:
        bool: True if successful, False if not found or error

    Example:
        update_user(1, username='Jane Doe', role='admin')
    """
    if not kwargs:
        print("Warning: No columns to update")
        return False

    if retrieve_user(user_id) is None:
        print(f"Error: User {user_id} not found")
        return False

    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        set_clause = ", ".join([f"{col} = ?" for col in kwargs.keys()])
        values = list(kwargs.values()) + [user_id]

        query = f"UPDATE realpage_user SET {set_clause} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()

        if success:
            print(f"✓ Updated user {user_id}")
        return success

    except Exception as e:
        conn.close()
        print(f"Error updating user: {e}")
        return False


# Example usage
if __name__ == "__main__":
    print("RealPage User Database Helper Functions")
    print("=" * 50)

    # Test 1: Get next user ID
    print("\n1. Get next user ID:")
    next_id = last_row_db()
    print(f"   Next available ID: {next_id}")

    # Test 2: Insert a user (commented out to avoid accidental inserts)
    # print("\n2. Insert user (example - not executed):")
    # print("   user_id = insert_user(")
    # print("       username='John Doe',")
    # print("       email='john@realpage.com',")
    # print("       password_hash='$2b$12$hashed_password',")
    # print("       role='realpage_user'")
    # print("   )")

    # Test 3: Retrieve by email (if any users exist)
    # user = retrieve_user_by_email('john@realpage.com')
    # if user:
    #     print(f"Found user: {user['username']}")

    print("\n" + "=" * 50)
    print("Tests complete!")
