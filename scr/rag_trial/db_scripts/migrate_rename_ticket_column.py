"""
Migration script to rename ticket_number column to ticket_id
This preserves all existing data while updating the schema.
"""

import sqlite3
from pathlib import Path


def migrate():
    """Rename ticket_number to ticket_id in the ticket table"""

    # Define database path
    script_dir = Path(__file__).parent
    db_path = script_dir.parent / "databases" / "realpage.db"

    print(f"Migrating database: {db_path}")

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = OFF")

    try:
        # Check current ticket count
        cursor.execute("SELECT COUNT(*) FROM ticket")
        ticket_count = cursor.fetchone()[0]
        print(f"Found {ticket_count} existing tickets")

        # Create new ticket table with ticket_id column
        print("\nCreating new table structure...")
        cursor.execute("""
            CREATE TABLE ticket_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id VARCHAR(50) UNIQUE NOT NULL,
                conversation_id VARCHAR(100) NOT NULL,
                channel VARCHAR(50),
                customer_role VARCHAR(100),
                product VARCHAR(100),
                transcript TEXT,
                first_tier_agent VARCHAR(100),
                status VARCHAR(20) DEFAULT 'pending',
                created_by INTEGER,
                assigned_to INTEGER,
                original_resolution TEXT,
                edited_resolution TEXT,
                relevancy_score FLOAT,
                reference_articles TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME,
                resolved_at DATETIME,
                FOREIGN KEY (created_by) REFERENCES realpage_user(id),
                FOREIGN KEY (assigned_to) REFERENCES support_agent(id)
            )
        """)

        # Copy all data from old table to new table
        print("Copying data from old table to new table...")
        cursor.execute("""
            INSERT INTO ticket_new (
                id, ticket_id, conversation_id, channel, customer_role,
                product, transcript, first_tier_agent, status, created_by,
                assigned_to, original_resolution, edited_resolution,
                relevancy_score, reference_articles, created_at,
                updated_at, resolved_at
            )
            SELECT 
                id, ticket_number, conversation_id, channel, customer_role,
                product, transcript, first_tier_agent, status, created_by,
                assigned_to, original_resolution, edited_resolution,
                relevancy_score, reference_articles, created_at,
                updated_at, resolved_at
            FROM ticket
        """)

        # Verify data was copied
        cursor.execute("SELECT COUNT(*) FROM ticket_new")
        new_count = cursor.fetchone()[0]
        print(f"Copied {new_count} tickets to new table")

        if new_count != ticket_count:
            raise Exception(
                f"Data mismatch! Original: {ticket_count}, New: {new_count}")

        # Drop old table
        print("Dropping old table...")
        cursor.execute("DROP TABLE ticket")

        # Rename new table to ticket
        print("Renaming new table to 'ticket'...")
        cursor.execute("ALTER TABLE ticket_new RENAME TO ticket")

        # Recreate indexes
        print("Recreating indexes...")
        cursor.execute("CREATE INDEX idx_ticket_id ON ticket(ticket_id)")
        cursor.execute("CREATE INDEX idx_ticket_status ON ticket(status)")
        cursor.execute(
            "CREATE INDEX idx_ticket_created_by ON ticket(created_by)")
        cursor.execute(
            "CREATE INDEX idx_ticket_assigned_to ON ticket(assigned_to)")

        # Commit changes
        conn.commit()

        # Verify final state
        cursor.execute("PRAGMA table_info(ticket)")
        columns = cursor.fetchall()
        print("\n✓ Migration successful!")
        print(f"  New columns: {[col[1] for col in columns]}")

        cursor.execute("SELECT COUNT(*) FROM ticket")
        final_count = cursor.fetchone()[0]
        print(f"  Final ticket count: {final_count}")

    except Exception as e:
        conn.rollback()
        print(f"\n✗ Migration failed: {e}")
        raise
    finally:
        cursor.execute("PRAGMA foreign_keys = ON")
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("MIGRATION: Rename ticket_number to ticket_id")
    print("=" * 60)
    migrate()
    print("=" * 60)
    print("Migration complete!")
