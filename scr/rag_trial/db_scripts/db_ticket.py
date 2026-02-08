"""
Database helper functions for ticket table
Simple CRUD operations for managing tickets.
"""

import sqlite3
from pathlib import Path
from datetime import datetime


def get_db_path():
    """Get the path to realpage.db"""
    script_dir = Path(__file__).parent
    return script_dir.parent / "databases" / "realpage.db"


def last_row_db():
    """
    Get the next available ticket ID.

    Returns:
        str: Next ticket ID in format 'CS-XXXXXXXX' (e.g., 'CS-12345678')
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all ticket_ids and find the max numerically
    cursor.execute("""
        SELECT ticket_id 
        FROM ticket 
        WHERE ticket_id LIKE 'CS-%'
    """)

    results = cursor.fetchall()
    conn.close()

    if results:
        # Extract numeric parts and find max
        numbers = [int(row[0].split('-')[1]) for row in results]
        max_num = max(numbers)
        new_num = max_num + 1
    else:
        # No tickets yet, start from 1
        new_num = 1

    # Format as 'CS-XXXXXXXX'
    new_ticket_id = f"CS-{new_num:08d}"
    return new_ticket_id


def retrieve_ticket(ticket_id):
    """
    Retrieve a ticket by its ID.

    Args:
        ticket_id (int): Ticket ID to retrieve

    Returns:
        dict: Ticket data with all columns, or None if not found
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM ticket WHERE id = ?", (ticket_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def retrieve_ticket_by_id_string(ticket_id):
    """
    Retrieve a ticket by its ticket_id string.

    Args:
        ticket_id (str): Ticket ID (e.g., 'CS-12345678')

    Returns:
        dict: Ticket data with all columns, or None if not found
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM ticket WHERE ticket_id = ?", (ticket_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def insert_ticket(**kwargs):
    """
    Insert a new ticket into the database.

    Args:
        **kwargs: Column names and values

    Returns:
        int: New ticket ID if successful, None if error

    Example:
        insert_ticket(
            ticket_id='CS-12345678',
            conversation_id='CONV-12345',
            channel='Chat',
            customer_role='Property Manager',
            product='RealPage Accounting',
            transcript='Customer: I need help...',
            status='pending',
            created_by=1
        )
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        columns = ", ".join(kwargs.keys())
        placeholders = ", ".join(["?" for _ in kwargs])
        values = list(kwargs.values())

        query = f"INSERT INTO ticket ({columns}) VALUES ({placeholders})"
        cursor.execute(query, values)
        conn.commit()

        new_id = cursor.lastrowid
        conn.close()

        print(f"✓ Inserted ticket with ID: {new_id}")
        return new_id

    except Exception as e:
        conn.close()
        print(f"Error inserting ticket: {e}")
        return None


def update_ticket(ticket_id, **kwargs):
    """
    Update a ticket by its ID.

    Args:
        ticket_id (int): Ticket ID to update
        **kwargs: Column names and values to update

    Returns:
        bool: True if successful, False if not found or error

    Example:
        update_ticket(1, status='approved', edited_resolution='Updated solution...')
    """
    if not kwargs:
        print("Warning: No columns to update")
        return False

    if retrieve_ticket(ticket_id) is None:
        print(f"Error: Ticket {ticket_id} not found")
        return False

    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        set_clause = ", ".join([f"{col} = ?" for col in kwargs.keys()])
        values = list(kwargs.values()) + [ticket_id]

        query = f"UPDATE ticket SET {set_clause} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()

        if success:
            print(f"✓ Updated ticket {ticket_id}")
        return success

    except Exception as e:
        conn.close()
        print(f"Error updating ticket: {e}")
        return False


def get_tickets_by_status(status):
    """
    Get all tickets with a specific status.

    Args:
        status (str): Status to filter by (e.g., 'pending', 'approved')

    Returns:
        list: List of ticket dictionaries
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM ticket WHERE status = ?", (status,))
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# Example usage
if __name__ == "__main__":
    print("Ticket Database Helper Functions")
    print("=" * 50)

    # Test 1: Get next ticket ID
    print("\n1. Get next ticket ID:")
    next_ticket = last_row_db()
    print(f"   Next available: {next_ticket}")

    # Test 2: Insert a ticket (commented out to avoid accidental inserts)
    # print("\n2. Insert ticket (example - not executed):")
    # print("   ticket_id = insert_ticket(")
    # print("       ticket_id='CS-12345678',")
    # print("       conversation_id='CONV-12345',")
    # print("       channel='Chat',")
    # print("       status='pending',")
    # print("       created_by=1")
    # print("   )")

    # Test 3: Get tickets by status
    print("\n3. Get tickets by status:")
    pending = get_tickets_by_status('pending')
    print(f"   Pending tickets: {len(pending)}")

    print("\n" + "=" * 50)
    print("Tests complete!")
