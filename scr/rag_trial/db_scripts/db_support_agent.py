"""
Database helper functions for support_agent table
Simple CRUD operations for managing support agents.
"""

import sqlite3
from pathlib import Path


def get_db_path():
    """Get the path to realpage.db"""
    script_dir = Path(__file__).parent
    return script_dir.parent / "databases" / "realpage.db"


def last_row_db():
    """
    Get the next available agent ID.

    Returns:
        int: Next agent ID (e.g., 1, 2, 3...)
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(id) FROM support_agent")
    result = cursor.fetchone()
    conn.close()

    if result[0]:
        return result[0] + 1
    return 1


def retrieve_agent(agent_id):
    """
    Retrieve a support agent by their ID.

    Args:
        agent_id (int): Agent ID to retrieve

    Returns:
        dict: Agent data with all columns, or None if not found
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM support_agent WHERE id = ?", (agent_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def retrieve_agent_by_email(email):
    """
    Retrieve a support agent by their email.

    Args:
        email (str): Agent email

    Returns:
        dict: Agent data with all columns, or None if not found
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM support_agent WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def insert_agent(**kwargs):
    """
    Insert a new support agent into the database.

    Args:
        **kwargs: Column names and values

    Returns:
        int: New agent ID if successful, None if error

    Example:
        insert_agent(
            username='Alex',
            email='alex@realpage.com',
            password_hash='$2b$12$...',
            agent_id='Agent3',
            tier='Tier3'
        )
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        columns = ", ".join(kwargs.keys())
        placeholders = ", ".join(["?" for _ in kwargs])
        values = list(kwargs.values())

        query = f"INSERT INTO support_agent ({columns}) VALUES ({placeholders})"
        cursor.execute(query, values)
        conn.commit()

        new_id = cursor.lastrowid
        conn.close()

        print(f"✓ Inserted agent with ID: {new_id}")
        return new_id

    except Exception as e:
        conn.close()
        print(f"Error inserting agent: {e}")
        return None


def update_agent(agent_id, **kwargs):
    """
    Update a support agent by their ID.

    Args:
        agent_id (int): Agent ID to update
        **kwargs: Column names and values to update

    Returns:
        bool: True if successful, False if not found or error

    Example:
        update_agent(1, username='Alex Smith', tier='Tier2')
    """
    if not kwargs:
        print("Warning: No columns to update")
        return False

    if retrieve_agent(agent_id) is None:
        print(f"Error: Agent {agent_id} not found")
        return False

    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        set_clause = ", ".join([f"{col} = ?" for col in kwargs.keys()])
        values = list(kwargs.values()) + [agent_id]

        query = f"UPDATE support_agent SET {set_clause} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()

        if success:
            print(f"✓ Updated agent {agent_id}")
        return success

    except Exception as e:
        conn.close()
        print(f"Error updating agent: {e}")
        return False


# Example usage
if __name__ == "__main__":
    print("Support Agent Database Helper Functions")
    print("=" * 50)

    # Test 1: Get next agent ID
    print("\n1. Get next agent ID:")
    next_id = last_row_db()
    print(f"   Next available ID: {next_id}")

    # Test 2: Insert an agent (commented out to avoid accidental inserts)
    # print("\n2. Insert agent (example - not executed):")
    # print("   agent_id = insert_agent(")
    # print("       username='Alex',")
    # print("       email='alex@realpage.com',")
    # print("       password_hash='$2b$12$hashed_password',")
    # print("       agent_id='Agent3',")
    # print("       tier='Tier3'")
    # print("   )")

    print("\n" + "=" * 50)
    print("Tests complete!")
