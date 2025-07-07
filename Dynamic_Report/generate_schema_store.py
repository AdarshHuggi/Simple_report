# generate_schema_store.py
import sqlite3

def generate_schema_from_db(db_path: str = "tableau_sim.db") -> dict:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Get table names
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cur.fetchall()]

    schema_store = {}

    for table in tables:
        # Get column info
        cur.execute(f"PRAGMA table_info({table});")
        columns = cur.fetchall()  # (cid, name, type, notnull, default, pk)

        field_dict = {col[1]: col[2] for col in columns}
        pk = next((col[1] for col in columns if col[5] == 1), None)

        schema_store[table] = {
            "fields": field_dict,
            "primary_key": pk
        }

    conn.close()
    return schema_store
