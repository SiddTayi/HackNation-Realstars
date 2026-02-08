"""
Database helper functions for new_knowledge table in realpage.db
Tracks approved resolutions added to the knowledge base.
"""

import sqlite3
from pathlib import Path


def get_db_path():
    """Get the path to realpage.db"""
    script_dir = Path(__file__).parent
    return script_dir.parent.parent.parent / "databases" / "realpage.db"


def last_row_db():
    """
    Generate the next available knowledge_id.

    Returns:
        str: Next knowledge_id in format 'KB-NEW-XXXX'
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT knowledge_id FROM new_knowledge
        WHERE knowledge_id LIKE 'KB-NEW-%'
        ORDER BY id DESC LIMIT 1
    """)
    result = cursor.fetchone()
    conn.close()

    if result:
        try:
            last_num = int(result[0].split("-")[-1])
            new_num = last_num + 1
        except (ValueError, IndexError):
            new_num = 1
    else:
        new_num = 1

    return f"KB-NEW-{new_num:04d}"


def insert_new_knowledge(**kwargs):
    """
    Insert a new row into the new_knowledge table.

    Args:
        **kwargs: Column names and values. Must include 'knowledge_id' and 'resolution'.

    Returns:
        bool: True if insert successful, False otherwise

    Example:
        insert_new_knowledge(
            knowledge_id='KB-NEW-0001',
            ticket_id=1,
            conversation_id='CONV-12345',
            product='RealPage Accounting',
            resolution='Approved resolution text...',
            reference_articles='["KB-001", "KB-023"]',
            created_by=1
        )
    """
    if "knowledge_id" not in kwargs:
        print("Error: knowledge_id is required")
        return False
    if "resolution" not in kwargs:
        print("Error: resolution is required")
        return False

    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        columns = ", ".join(kwargs.keys())
        placeholders = ", ".join(["?" for _ in kwargs])
        values = list(kwargs.values())

        query = f"INSERT INTO new_knowledge ({columns}) VALUES ({placeholders})"
        cursor.execute(query, values)
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()

        if success:
            print(f"  Inserted new_knowledge '{kwargs['knowledge_id']}'")
        return success

    except Exception as e:
        conn.close()
        print(f"Error inserting new_knowledge: {e}")
        return False


def retrieve_new_knowledge(knowledge_id):
    """
    Retrieve a new_knowledge row by its knowledge_id.

    Args:
        knowledge_id (str): e.g. 'KB-NEW-0001'

    Returns:
        dict or None
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM new_knowledge WHERE knowledge_id = ?",
        (knowledge_id,),
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def list_new_knowledge():
    """
    List all rows from the new_knowledge table, newest first.

    Returns:
        list[dict]: All new_knowledge rows
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM new_knowledge ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()

    return [dict(r) for r in rows]


if __name__ == "__main__":
    print("new_knowledge Database Helper")
    print("=" * 40)
    print(f"DB path: {get_db_path()}")
    print(f"Next ID: {last_row_db()}")
    print(f"Rows:    {len(list_new_knowledge())}")
