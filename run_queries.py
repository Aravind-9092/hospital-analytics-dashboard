import sqlite3

conn = sqlite3.connect("hospital.db")
cursor = conn.cursor()

with open("queries.sql", "r") as f:
    sql_script = f.read()

# Split on the numbered comment blocks isn't reliable, so just run each statement separately
queries = [q.strip() for q in sql_script.split(";") if q.strip() and not q.strip().startswith("--")]

for i, query in enumerate(queries, 1):
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        print(f"\n--- Query {i} ---")
        print(f"Rows returned: {len(rows)}")
        if rows:
            print("Sample row:", rows[0])
    except Exception as e:
        print(f"\n--- Query {i} FAILED ---")
        print(e)

conn.close()