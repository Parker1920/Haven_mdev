import sqlite3

conn = sqlite3.connect('C:/Users/parke/OneDrive/Desktop/Haven_mdev/data/VH-Database.db')
cursor = conn.cursor()

# Count total
cursor.execute('SELECT COUNT(*) FROM discoveries')
count = cursor.fetchone()[0]
print(f'Total discoveries in database: {count}')

# Get recent ones
cursor.execute('''
    SELECT id, discovery_type, description, discovered_by, submission_timestamp
    FROM discoveries
    ORDER BY id DESC
    LIMIT 5
''')
recent = cursor.fetchall()

if recent:
    print(f'\nMost recent {len(recent)} discoveries:')
    for r in recent:
        desc = r[2][:50] if r[2] else 'No description'
        print(f'  ID {r[0]}: {r[1]} - {desc}... by {r[3]} at {r[4]}')
else:
    print('\nNo discoveries found in database')

conn.close()
