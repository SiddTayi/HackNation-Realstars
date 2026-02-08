import os
import sys
import pandas as pd
import sqlite3
from pathlib import Path

def create_scripts_database():
    """
    Convert Scripts_Master sheet from Excel to SQLite database.
    Creates scripts.db with all script data indexed for fast lookups.
    """
    # Define paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent.parent
    excel_path = project_root / "data" / "SupportMind__Final_Data.xlsx"
    db_path = script_dir.parent / "databases" / "scripts.db"
    
    print(f"Reading Excel file: {excel_path}")
    
    # Read Scripts_Master sheet
    df = pd.read_excel(excel_path, sheet_name='Scripts_Master')
    print(f"Loaded {len(df)} rows from Scripts_Master sheet")
    
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
        CREATE TABLE scripts_master (
            Script_ID TEXT PRIMARY KEY,
            Script_Title TEXT,
            Script_Purpose TEXT,
            Script_Inputs TEXT,
            Module TEXT,
            Category TEXT,
            Source TEXT,
            Script_Text_Sanitized TEXT
        )
    ''')
    
    print("Created scripts_master table")
    
    # Insert data
    print("Inserting data...")
    for idx, row in df.iterrows():
        cursor.execute('''
            INSERT INTO scripts_master (
                Script_ID, Script_Title, Script_Purpose, Script_Inputs,
                Module, Category, Source, Script_Text_Sanitized
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row['Script_ID'],
            row['Script_Title'],
            row['Script_Purpose'],
            row['Script_Inputs'],
            row['Module'],
            row['Category'],
            row['Source'],
            row['Script_Text_Sanitized']
        ))
    
    # Create index for fast lookups
    cursor.execute('CREATE INDEX idx_script_id ON scripts_master(Script_ID)')
    cursor.execute('CREATE INDEX idx_module ON scripts_master(Module)')
    cursor.execute('CREATE INDEX idx_category ON scripts_master(Category)')
    
    print("Created indexes on Script_ID, Module, and Category")
    
    # Commit and close
    conn.commit()
    
    # Verify
    cursor.execute('SELECT COUNT(*) FROM scripts_master')
    count = cursor.fetchone()[0]
    print(f"\n✓ Successfully created scripts.db with {count} rows")
    
    # Show sample data
    cursor.execute('SELECT Script_ID, Script_Title, Module FROM scripts_master LIMIT 3')
    samples = cursor.fetchall()
    print("\nSample data:")
    for sample in samples:
        print(f"  {sample[0]} - {sample[1]} ({sample[2]})")
    
    conn.close()
    print(f"\n✓ Database saved to: {db_path}")

if __name__ == "__main__":
    create_scripts_database()
