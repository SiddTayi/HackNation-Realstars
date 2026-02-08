"""
Script to re-import all tickets with all columns from Excel
This will clear existing tickets and re-import with all data
"""

import pandas as pd
import sqlite3
from pathlib import Path


def reimport_tickets():
    """Clear and re-import all tickets with full data"""

    # Paths
    excel_path = Path(__file__).parent.parent.parent.parent / \
        "data" / "final_ver3.xlsx"
    db_path = Path(__file__).parent.parent / "databases" / "realpage.db"

    print(f"Reading Excel: {excel_path}")
    df = pd.read_excel(excel_path)

    # Remove duplicates
    df = df.drop_duplicates(subset='Ticket_Number', keep='first')
    print(f"Loaded {len(df)} unique tickets from Excel")

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Clear existing tickets
        print("\nClearing existing tickets...")
        cursor.execute("DELETE FROM ticket")
        print("✓ Cleared")

        # Import all tickets with all columns
        print(f"\nImporting {len(df)} tickets with all columns...")
        imported_count = 0

        for idx, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO ticket (
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
                    'pending',
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

                if (imported_count % 50) == 0:
                    print(f"  Imported {imported_count}...")

            except Exception as e:
                print(f"Error importing {row['Ticket_Number']}: {e}")

        conn.commit()

        # Verify
        cursor.execute("SELECT COUNT(*) FROM ticket")
        final_count = cursor.fetchone()[0]

        print(f"\n✓ Successfully imported {imported_count} tickets")
        print(f"✓ Database contains {final_count} tickets")

        # Show sample with new columns
        print("\nSample record with new columns:")
        cursor.execute("""
            SELECT ticket_id, category, sentiment, priority, tier, answer_type 
            FROM ticket LIMIT 1
        """)
        sample = cursor.fetchone()
        if sample:
            print(f"  ticket_id: {sample[0]}")
            print(f"  category: {sample[1]}")
            print(f"  sentiment: {sample[2]}")
            print(f"  priority: {sample[3]}")
            print(f"  tier: {sample[4]}")
            print(f"  answer_type: {sample[5]}")

    except Exception as e:
        conn.rollback()
        print(f"\n✗ Import failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("RE-IMPORT: All tickets with all columns")
    print("=" * 60)

    response = input(
        "\nThis will DELETE all existing tickets and re-import.\nContinue? (yes/no): ")

    if response.lower() == 'yes':
        reimport_tickets()
        print("=" * 60)
        print("Re-import complete!")
    else:
        print("Cancelled.")
