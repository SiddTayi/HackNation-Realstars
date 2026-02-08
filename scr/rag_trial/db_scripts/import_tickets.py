import pandas as pd
import sqlite3
from pathlib import Path

# Read Excel file
excel_path = "/HackNation-Realstars/data/final_ver3.xlsx"
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
                status, category, issue_summary, sentiment, priority, tier,
                module_generated_kb, subject, description, root_cause,
                tags_generated_kb, kb_article_id, script_id, 
                generated_kb_article_id, source_id, answer_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row['Ticket_Number'],
            row['Conversation_ID'],
            row.get('Channel'),
            row.get('Customer_Role'),
            row.get('Product_x'),
            row.get('Transcript'),
            row.get('Agent_Name'),
            row.get('Resolution'),
            'pending',  # status
            row.get('Category_x'),
            row.get('Issue_Summary'),
            row.get('Sentiment'),
            row.get('Priority'),
            row.get('Tier'),
            row.get('Module_generated_kb'),
            row.get('Subject'),
            row.get('Description'),
            row.get('Root_Cause'),
            row.get('Tags_generated_kb'),
            row.get('KB_Article_ID_x'),
            row.get('Script_ID'),
            row.get('Generated_KB_Article_ID'),
            row.get('Source_ID'),
            row.get('Answer_Type')
        ))
        imported_count += 1
    except Exception as e:
        print(f"Error importing {row['Ticket_Number']}: {e}")

conn.commit()
conn.close()
print(f"✓ Imported {imported_count} tickets")
