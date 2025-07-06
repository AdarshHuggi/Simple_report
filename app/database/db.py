import sqlite3
from datetime import datetime

DB_PATH = "f:/projects/report_app/app/database/report_app.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def create_tables_and_insert_data():
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE
    )
    """)

    # Reports table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        report_id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_name TEXT NOT NULL,
        created_on TEXT NOT NULL,
        owner_id INTEGER,
        FOREIGN KEY (owner_id) REFERENCES users(user_id)
    )
    """)

    # Sessions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        report_id INTEGER,
        started_on TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (report_id) REFERENCES reports(report_id)
    )
    """)

    # Selections table (fields/tables selected in a session)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS selections (
        selection_id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        table_name TEXT NOT NULL,
        field_name TEXT NOT NULL,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id)
    )
    """)

    # Mapping table for dynamic SQL query generation
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS table_mappings (
        mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_table TEXT NOT NULL,
        target_table TEXT NOT NULL,
        relation_type TEXT NOT NULL, -- e.g., 'one-to-many', 'many-to-one', 'many-to-many'
        join_condition TEXT NOT NULL
    )
    """)

    # Insert 10 users
    for i in range(1, 11):
        try:
            cursor.execute("INSERT INTO users (username) VALUES (?)", (f"user{i}",))
        except sqlite3.IntegrityError:
            pass  # Skip if already exists

    # Insert 10 reports
    for i in range(1, 11):
        cursor.execute(
            "INSERT OR IGNORE INTO reports (report_name, created_on, owner_id) VALUES (?, ?, ?)",
            (f"Report {i}", datetime.now().isoformat(), (i % 10) + 1)
        )

    # Insert 10 sessions
    for i in range(1, 11):
        cursor.execute(
            "INSERT OR IGNORE INTO sessions (user_id, report_id, started_on) VALUES (?, ?, ?)",
            ((i % 10) + 1, (i % 10) + 1, datetime.now().isoformat())
        )

    # Insert 10 selections
    for i in range(1, 11):
        cursor.execute(
            "INSERT OR IGNORE INTO selections (session_id, table_name, field_name) VALUES (?, ?, ?)",
            ((i % 10) + 1, f"table_{i}", f"field_{i}")
        )

    # Insert 10 mapping records
    for i in range(1, 11):
        cursor.execute(
            "INSERT OR IGNORE INTO table_mappings (source_table, target_table, relation_type, join_condition) VALUES (?, ?, ?, ?)",
            (
                f"table_{i}",
                f"table_{(i % 10) + 1}",
                "one-to-many" if i % 2 == 0 else "many-to-one",
                f"table_{i}.id = table_{(i % 10) + 1}.ref_id"
            )
        )

    conn.commit()
    conn.close()
