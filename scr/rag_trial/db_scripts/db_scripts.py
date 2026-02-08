"""
Database helper functions for scripts.db
Simple CRUD operations for managing scripts.
"""

import sqlite3
from pathlib import Path


def get_db_path():
    """Get the path to scripts.db"""
    script_dir = Path(__file__).parent
    return script_dir.parent / "databases" / "scripts.db"


def last_row_db():
    """
    Get the next available Script_ID by finding the last one and incrementing.

    Returns:
        str: Next Script_ID in format 'SCRIPT-XXXX' (e.g., 'SCRIPT-0715')

    Note: For a better approach, you could use SQLite's autoincrement,
    but since Script_ID is text-based, this manual approach works well.
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get the highest Script_ID number
    cursor.execute("""
        SELECT Script_ID 
        FROM scripts_master 
        WHERE Script_ID LIKE 'SCRIPT-%' 
        ORDER BY Script_ID DESC 
        LIMIT 1
    """)

    result = cursor.fetchone()
    conn.close()

    if result:
        last_id = result[0]
        # Extract number from 'SCRIPT-0714' -> 714
        last_num = int(last_id.split('-')[1])
        new_num = last_num + 1
    else:
        # No scripts found, start from 1
        new_num = 1

    # Format as 'SCRIPT-0001'
    new_script_id = f"SCRIPT-{new_num:04d}"
    return new_script_id


def retrieve_script(script_id):
    """
    Retrieve a script by its Script_ID.

    Args:
        script_id (str): Script_ID to retrieve (e.g., 'SCRIPT-0001')

    Returns:
        dict: Script data with all columns, or None if not found
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM scripts_master
        WHERE Script_ID = ?
    """, (script_id,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def update_script(script_id, **kwargs):
    """
    Update a script by its Script_ID.
    Accepts any column names dynamically.

    Args:
        script_id (str): Script_ID to update
        **kwargs: Column names and values to update (any columns in the table)

    Returns:
        bool: True if update successful, False if script not found or error

    Example:
        update_script('SCRIPT-0001', Script_Title='New Title', Module='New Module')
    """
    if not kwargs:
        print("Warning: No columns to update")
        return False

    # Check if script exists
    if retrieve_script(script_id) is None:
        print(f"Error: Script '{script_id}' not found")
        return False

    # Build UPDATE query dynamically
    set_clause = ", ".join([f"{col} = ?" for col in kwargs.keys()])
    values = list(kwargs.values()) + [script_id]

    query = f"""
        UPDATE scripts_master
        SET {set_clause}
        WHERE Script_ID = ?
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
            print(f"✓ Updated script '{script_id}'")
        return success

    except Exception as e:
        conn.close()
        print(f"Error updating script: {e}")
        return False


def insert_script(**kwargs):
    """
    Insert a new script into the database.
    Accepts any column names dynamically.

    Args:
        **kwargs: Column names and values (must include 'Script_ID')

    Returns:
        bool: True if insert successful, False if script already exists or error

    Example:
        insert_script(
            Script_ID='SCRIPT-0715',
            Script_Title='New Script',
            Script_Purpose='Does something useful',
            Script_Inputs='<DATABASE>',
            Module='Testing',
            Category='Test',
            Source='SELF_HEALING',
            Script_Text_Sanitized='SELECT * FROM test;'
        )
    """
    if 'Script_ID' not in kwargs:
        print("Error: Script_ID is required")
        return False

    script_id = kwargs['Script_ID']

    # Check if script already exists
    if retrieve_script(script_id) is not None:
        print(f"Error: Script '{script_id}' already exists")
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
            INSERT INTO scripts_master ({columns})
            VALUES ({placeholders})
        """

        cursor.execute(query, values)
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()

        if success:
            print(f"✓ Inserted script '{script_id}'")
        return success

    except Exception as e:
        conn.close()
        print(f"Error inserting script: {e}")
        return False


# Example usage
if __name__ == "__main__":
    print("Script Database Helper Functions")
    print("=" * 50)

    # Test 1: Get next Script_ID
    print("\n1. Get next Script_ID:")
    next_id = last_row_db()
    print(f"   Next available ID: {next_id}")

    # Test 2: Retrieve a script
    print("\n2. Retrieve existing script:")
    script = retrieve_script('SCRIPT-0001')
    if script:
        print(f"   Found: {script['Script_ID']}")
        print(f"   Title: {script['Script_Title']}")
        print(f"   Module: {script['Module']}")
    else:
        print("   Script not found")

    # Test 3: Update a script (commented out to avoid accidental updates)
    # print("\n3. Update script (example - not executed):")
    # print("   update_script('SCRIPT-0001', Script_Title='Updated Title')")

    # Test 4: Insert a script (commented out to avoid accidental inserts)
    # print("\n4. Insert script (example - not executed):")
    # print("   insert_script(")
    # print("       Script_ID='SCRIPT-9999',")
    # print("       Script_Title='Test Script',")
    # print("       Script_Purpose='Testing insertion',")
    # print("       Script_Inputs='<DATABASE>',")
    # print("       Module='Testing',")
    # print("       Category='Test',")
    # print("       Source='MANUAL',")
    # print("       Script_Text_Sanitized='SELECT 1;'")
    # print("   )")

    print("\n" + "=" * 50)
    print("Tests complete!")
