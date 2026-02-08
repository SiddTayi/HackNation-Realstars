import os
import sys
import pandas as pd
import sqlite3
from pathlib import Path

def create_kb_database():
    """
    Convert Knowledge_Articles sheet from Excel to SQLite database.
    Creates knowledge_articles.db with all KB data indexed for fast lookups.
    """
    # Define paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent.parent
    excel_path = project_root / "data" / "SupportMind__Final_Data.xlsx"
    db_path = script_dir.parent / "databases" / "knowledge_articles.db"
    
    print(f"Reading Excel file: {excel_path}")
    
    # Read Knowledge_Articles sheet
    df = pd.read_excel(excel_path, sheet_name='Knowledge_Articles')
    print(f"Loaded {len(df)} rows from Knowledge_Articles sheet")
    
    # Display columns
    print(f"Columns: {df.columns.tolist()}")
    
    # Remove existing database if it exists
    if db_path.exists():
        print(f"Removing existing database: {db_path}")
        db_path.unlink()
    
    # Create database connection
    print(f"Creating SQLite database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
        CREATE TABLE knowledge_articles (
            KB_Article_ID TEXT PRIMARY KEY,
            Title TEXT,
            Body TEXT,
            Tags TEXT,
            Module TEXT,
            Category TEXT,
            Created_At TEXT,
            Updated_At TEXT,
            Status TEXT,
            Source_Type TEXT
        )
    ''')
    
    print("Created knowledge_articles table")
    
    # Insert data
    print("Inserting data...")
    for idx, row in df.iterrows():
        cursor.execute('''
            INSERT INTO knowledge_articles (
                KB_Article_ID, Title, Body, Tags, Module, Category,
                Created_At, Updated_At, Status, Source_Type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row['KB_Article_ID'],
            row['Title'],
            row['Body'],
            str(row['Tags']) if pd.notna(row['Tags']) else None,
            str(row['Module']) if pd.notna(row['Module']) else None,
            str(row['Category']) if pd.notna(row['Category']) else None,
            str(row['Created_At']) if pd.notna(row['Created_At']) else None,
            str(row['Updated_At']) if pd.notna(row['Updated_At']) else None,
            row['Status'],
            row['Source_Type']
        ))
    
    # Create indexes for fast lookups
    cursor.execute('CREATE INDEX idx_kb_article_id ON knowledge_articles(KB_Article_ID)')
    cursor.execute('CREATE INDEX idx_kb_module ON knowledge_articles(Module)')
    cursor.execute('CREATE INDEX idx_kb_category ON knowledge_articles(Category)')
    cursor.execute('CREATE INDEX idx_kb_status ON knowledge_articles(Status)')
    
    print("Created indexes on KB_Article_ID, Module, Category, and Status")
    
    # Commit and close
    conn.commit()
    
    # Verify
    cursor.execute('SELECT COUNT(*) FROM knowledge_articles')
    count = cursor.fetchone()[0]
    print(f"\n✓ Successfully created knowledge_articles.db with {count} rows")
    
    # Show sample data
    cursor.execute('SELECT KB_Article_ID, Title, Status FROM knowledge_articles LIMIT 3')
    samples = cursor.fetchall()
    print("\nSample data:")
    for sample in samples:
        print(f"  {sample[0]} - {sample[1][:50]}... ({sample[2]})")
    
    conn.close()
    print(f"\n✓ Database saved to: {db_path}")

if __name__ == "__main__":
    create_kb_database()
