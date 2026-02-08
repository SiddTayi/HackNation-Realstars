"""
Create 3 tables: realpage_user, support_agent, ticket
Simple script to initialize realpage.db with all required tables.
"""

import sqlite3
from pathlib import Path


def create_tables():
    """Create all tables in realpage.db"""

    # Define database path
    script_dir = Path(__file__).parent
    db_path = script_dir.parent / "databases" / "realpage.db"

    print(f"Creating database: {db_path}")

    # Remove existing database if it exists
    if db_path.exists():
        print(f"Removing existing database...")
        db_path.unlink()

    # Create connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")

    print("\nCreating tables...")

    # Table 1: realpage_user
    cursor.execute("""
        CREATE TABLE realpage_user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(100) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(50) DEFAULT 'realpage_user',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX idx_user_email ON realpage_user(email)")
    print("✓ Created realpage_user table")

    # Table 2: support_agent
    cursor.execute("""
        CREATE TABLE support_agent (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(100) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            agent_id VARCHAR(50) UNIQUE NOT NULL,
            tier VARCHAR(20) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX idx_agent_email ON support_agent(email)")
    cursor.execute("CREATE INDEX idx_agent_id ON support_agent(agent_id)")
    print("✓ Created support_agent table")

    # Table 3: ticket
    cursor.execute("""
        CREATE TABLE ticket (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_number VARCHAR(50) UNIQUE NOT NULL,
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
    cursor.execute("CREATE INDEX idx_ticket_number ON ticket(ticket_number)")
    cursor.execute("CREATE INDEX idx_ticket_status ON ticket(status)")
    cursor.execute("CREATE INDEX idx_ticket_created_by ON ticket(created_by)")
    cursor.execute(
        "CREATE INDEX idx_ticket_assigned_to ON ticket(assigned_to)")
    print("✓ Created ticket table")

    # Commit changes
    conn.commit()

    # Verify tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    print(f"\n✓ Database created successfully!")
    print(f"  Location: {db_path}")
    print(f"  Tables: {[t[0] for t in tables]}")

    # Show table info
    for table_name in ['realpage_user', 'support_agent', 'ticket']:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print(f"\n  {table_name}: {len(columns)} columns")

    conn.close()
    print("\n✓ All tables created!")


if __name__ == "__main__":
    create_tables()
