"""
Migration script to add all missing columns from Excel to ticket table
"""

import sqlite3
from pathlib import Path


def migrate():
    """Add missing columns to ticket table"""

    script_dir = Path(__file__).parent
    db_path = script_dir.parent / "databases" / "realpage.db"

    print(f"Migrating database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check current columns
        cursor.execute("PRAGMA table_info(ticket)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        print(f"\nExisting columns: {len(existing_columns)}")

        # New columns to add (mapping Excel -> DB)
        new_columns = [
            ("category", "VARCHAR(100)"),
            ("issue_summary", "TEXT"),
            ("sentiment", "VARCHAR(50)"),
            ("priority", "VARCHAR(20)"),
            ("tier", "VARCHAR(20)"),
            ("module_generated_kb", "VARCHAR(100)"),
            ("subject", "TEXT"),
            ("description", "TEXT"),
            ("root_cause", "TEXT"),
            ("tags_generated_kb", "TEXT"),
            ("kb_article_id", "VARCHAR(50)"),
            ("script_id", "VARCHAR(50)"),
            ("generated_kb_article_id", "VARCHAR(50)"),
            ("source_id", "VARCHAR(50)"),
            ("answer_type", "VARCHAR(50)")
        ]

        print(f"Adding {len(new_columns)} new columns...")

        for col_name, col_type in new_columns:
            if col_name not in existing_columns:
                print(f"  Adding column: {col_name} ({col_type})")
                cursor.execute(
                    f"ALTER TABLE ticket ADD COLUMN {col_name} {col_type}")

        conn.commit()

        # Verify final schema
        cursor.execute("PRAGMA table_info(ticket)")
        final_columns = cursor.fetchall()
        print(f"\n✓ Migration successful!")
        print(f"  Total columns: {len(final_columns)}")
        print(f"\nAll columns:")
        for col in final_columns:
            print(f"  {col[1]} ({col[2]})")

    except Exception as e:
        conn.rollback()
        print(f"\n✗ Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("MIGRATION: Add all Excel columns to ticket table")
    print("=" * 60)
    migrate()
    print("=" * 60)
    print("Migration complete!")
