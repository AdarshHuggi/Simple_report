# generate_relationships.py
import sqlite3
from relationships import TableRelationship

def generate_relationships_from_db(db_path="tableau_sim.db"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Get all table names
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cur.fetchall()]

    relationships = []

    for table in tables:
        # Get foreign keys in the table
        cur.execute(f"PRAGMA foreign_key_list({table})")
        for row in cur.fetchall():
            # row = (id, seq, table, from_col, to_col, on_update, on_delete, match)
            ref_table = row[2]
            from_col = row[3]
            to_col = row[4]

            relationships.append(
                TableRelationship(
                    left_table=table,
                    right_table=ref_table,
                    left_field=from_col,
                    right_field=to_col,
                    cardinality="many-to-one",
                    integrity="all-matching"
                )
            )

    conn.close()
    return relationships
