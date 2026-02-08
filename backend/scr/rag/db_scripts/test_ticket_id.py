from db_ticket import last_row_db
import sqlite3

# Connect and get top 5 highest ticket IDs
conn = sqlite3.connect('../databases/realpage.db')
cursor = conn.cursor()

# Get all ticket_ids sorted numerically
cursor.execute('SELECT ticket_id FROM ticket')
all_ids = cursor.fetchall()
conn.close()

# Extract numbers and sort
ticket_numbers = [(row[0], int(row[0].split('-')[1])) for row in all_ids]
ticket_numbers.sort(key=lambda x: x[1], reverse=True)

print('Top 5 highest ticket IDs (by numeric value):')
for ticket_id, num in ticket_numbers[:5]:
    print(f'  {ticket_id} (number: {num})')

print(f'\nNext ticket ID will be: {last_row_db()}')
