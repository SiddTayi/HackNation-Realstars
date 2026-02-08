"""
Database helper functions for knowledge_articles.db
Simple CRUD operations for managing knowledge articles.
"""

import sqlite3
from pathlib import Path


def get_db_path():
    """Get the path to knowledge_articles.db"""
    script_dir = Path(__file__).parent
    return script_dir.parent.parent.parent / "databases" / "knowledge_articles.db"


def last_row_db():
    """
    Get the next available KB_Article_ID using a UUID-based approach.

    Returns:
        str: Next KB_Article_ID in format 'KB-XXXXXXXX' (8-char hex UUID)

    Note: Since KB_Article_IDs have mixed formats (KB-SYN-XXXX, KB-XXXXXXXXXX, etc.),
    the best approach is to generate a unique UUID-based ID rather than incrementing.
    """
    import uuid

    # Generate a unique 8-character hex ID
    new_hex = uuid.uuid4().hex[:8].upper()
    new_kb_id = f"KB-{new_hex}"

    # Verify it doesn't already exist (very unlikely, but good practice)
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT KB_Article_ID 
        FROM knowledge_articles 
        WHERE KB_Article_ID = ?
    """, (new_kb_id,))

    result = cursor.fetchone()
    conn.close()

    # If by chance it exists, generate a new one (recursion)
    if result:
        return last_row_db()

    return new_kb_id


def retrieve_kb(kb_id):
    """
    Retrieve a knowledge article by its KB_Article_ID.

    Args:
        kb_id (str): KB_Article_ID to retrieve (e.g., 'KB-3FFBFE3C70')

    Returns:
        dict: KB article data with all columns, or None if not found
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM knowledge_articles
        WHERE KB_Article_ID = ?
    """, (kb_id,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def update_kb(kb_id, **kwargs):
    """
    Update a knowledge article by its KB_Article_ID.
    Accepts any column names dynamically.

    Args:
        kb_id (str): KB_Article_ID to update
        **kwargs: Column names and values to update (any columns in the table)

    Returns:
        bool: True if update successful, False if KB article not found or error

    Example:
        update_kb('KB-3FFBFE3C70', Title='New Title', Module='New Module')
    """
    if not kwargs:
        print("Warning: No columns to update")
        return False

    # Check if KB article exists
    if retrieve_kb(kb_id) is None:
        print(f"Error: KB article '{kb_id}' not found")
        return False

    # Build UPDATE query dynamically
    set_clause = ", ".join([f"{col} = ?" for col in kwargs.keys()])
    values = list(kwargs.values()) + [kb_id]

    query = f"""
        UPDATE knowledge_articles
        SET {set_clause}
        WHERE KB_Article_ID = ?
    """

    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute(query, values)
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()

        if success:
            print(f"✓ Updated KB article '{kb_id}'")
        return success

    except Exception as e:
        conn.close()
        print(f"Error updating KB article: {e}")
        return False


def insert_kb(**kwargs):
    """
    Insert a new knowledge article into the database.
    Accepts any column names dynamically.

    Args:
        **kwargs: Column names and values (must include 'KB_Article_ID')

    Returns:
        bool: True if insert successful, False if KB article already exists or error

    Example:
        from datetime import datetime
        now = datetime.now().isoformat()
        insert_kb(
            KB_Article_ID='KB-12345678',
            Title='How to Reset Password',
            Body='Step 1: Go to settings...',
            Tags='password, reset, security',
            Module='User Management',
            Category='Security',
            Created_At=now,
            Updated_At=now,
            Status='Active',
            Source_Type='SELF_HEALING'
        )
    """
    if 'KB_Article_ID' not in kwargs:
        print("Error: KB_Article_ID is required")
        return False

    kb_id = kwargs['KB_Article_ID']

    # Check if KB article already exists
    if retrieve_kb(kb_id) is not None:
        print(f"Error: KB article '{kb_id}' already exists")
        return False

    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Build INSERT query dynamically
        columns = ", ".join(kwargs.keys())
        placeholders = ", ".join(["?" for _ in kwargs])
        values = list(kwargs.values())

        query = f"""
            INSERT INTO knowledge_articles ({columns})
            VALUES ({placeholders})
        """

        cursor.execute(query, values)
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()

        if success:
            print(f"✓ Inserted KB article '{kb_id}'")
        return success

    except Exception as e:
        conn.close()
        print(f"Error inserting KB article: {e}")
        return False


# Example usage
if __name__ == "__main__":
    print("Knowledge Articles Database Helper Functions")
    print("=" * 50)

    # Test 1: Get next KB_Article_ID
    print("\n1. Get next KB_Article_ID:")
    next_id = last_row_db()
    print(f"   Next available ID: {next_id}")

    # Test 2: Retrieve a KB article
    print("\n2. Retrieve existing KB article:")
    kb = retrieve_kb('KB-3FFBFE3C70')
    if kb:
        print(f"   Found: {kb['KB_Article_ID']}")
        print(f"   Title: {kb['Title'][:60]}...")
        print(f"   Module: {kb['Module']}")
        print(f"   Status: {kb['Status']}")
    else:
        print("   KB article not found")

    # Test 3: Update a KB article (commented out to avoid accidental updates)
    # print("\n3. Update KB article (example - not executed):")
    # print("   update_kb('KB-3FFBFE3C70', Title='Updated Title')")

    # Test 4: Insert a KB article (commented out to avoid accidental inserts)
    # print("\n4. Insert KB article (example - not executed):")
    # from datetime import datetime
    # now = datetime.now().isoformat()
    # print("   insert_kb(")
    # print("       KB_Article_ID='KB-99999999',")
    # print("       Title='Test KB Article',")
    # print("       Body='This is a test article',")
    # print("       Tags='test, example',")
    # print("       Module='Testing',")
    # print("       Category='Test',")
    # print(f"       Created_At='{now}',")
    # print(f"       Updated_At='{now}',")
    # print("       Status='Active',")
    # print("       Source_Type='MANUAL'")
    # print("   )")

    print("\n" + "=" * 50)
    print("Tests complete!")
