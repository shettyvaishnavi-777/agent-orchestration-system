import sys

sys.path.insert(0, "1database")

from datab import get_connection


conn = get_connection()

cursor = conn.cursor()

cursor.execute(
    """
    INSERT INTO tasks
    (task, research, analysis, final_report)
    VALUES (%s, %s, %s, %s)
    """,
    (
        "Test PostgreSQL memory",
        "This is test research.",
        "This is test analysis.",
        "This is a test final report."
    )
)

conn.commit()

print("✅ Memory saved to PostgreSQL!")

cursor.execute(
    """
    SELECT id, task, created_at
    FROM tasks
    ORDER BY id DESC
    LIMIT 3
    """
)

rows = cursor.fetchall()

print("\nRecent memories:")

for row in rows:
    print(row)

cursor.close()
conn.close()

print("\n✅ PostgreSQL memory test completed!")