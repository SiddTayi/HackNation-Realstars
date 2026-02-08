import pandas as pd
import sqlite3
from pathlib import Path

# Read Excel file
excel_path = "/Users/faseehahmed26/Desktop/FaseehWorld/Interview Prep/realpage/Hackathon/HackNation-Realstars/data/final_ver3.xlsx"
df = pd.read_excel(excel_path)

# Remove duplicates based on Ticket_Number
df = df.drop_duplicates(subset='Ticket_Number', keep='first')
print(f"Loaded {len(df)} unique tickets from Excel")

# Connect to database
db_path = "/Users/faseehahmed26/Desktop/FaseehWorld/Interview Prep/realpage/Hackathon/HackNation-Realstars/scr/rag_trial/databases/realpage.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Import data
imported_count = 0
for _, row in df.iterrows():
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO ticket (
                ticket_id, conversation_id, channel, customer_role,
                product, transcript, first_tier_agent, original_resolution,
                status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending')
        """, (
            row['Ticket_Number'],
            row['Conversation_ID'],
            row.get('Channel'),
            row.get('Customer_Role'),
            row.get('Product_x'),
            row.get('Transcript'),
            row.get('Agent_Name'),
            row.get('Resolution')
        ))
        imported_count += 1
    except Exception as e:
        print(f"Error importing {row['Ticket_Number']}: {e}")

conn.commit()
conn.close()
print(f"✓ Imported {imported_count} tickets")
