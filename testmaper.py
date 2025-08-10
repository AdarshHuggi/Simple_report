


CREATE TABLE reports (
    report_id INTEGER PRIMARY KEY,
    report_name TEXT NOT NULL,
    base_table TEXT NOT NULL,
    select_clause TEXT NOT NULL,
    join_clause TEXT
);


CREATE TABLE report_filters (
    filter_id INTEGER PRIMARY KEY,
    report_id INTEGER NOT NULL,
    ui_filter_key TEXT NOT NULL,
    db_column TEXT NOT NULL,
    operator TEXT NOT NULL DEFAULT "=",
    FOREIGN KEY (report_id) REFERENCES reports(report_id)
);









import sqlite3
from fastapi import FastAPI, Query
from typing import Dict, Any

DB_PATH = "reports.db"
app = FastAPI()

def get_report_definition(report_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get SELECT, FROM, JOIN
    cursor.execute("SELECT select_clause, base_table, join_clause FROM reports WHERE report_id=?", (report_id,))
    report = cursor.fetchone()
    if not report:
        conn.close()
        return None
    
    select_clause, base_table, join_clause = report
    
    # Get filter mappings
    cursor.execute("SELECT ui_filter_key, db_column, operator FROM report_filters WHERE report_id=?", (report_id,))
    filters = {row[0]: {"column": row[1], "op": row[2]} for row in cursor.fetchall()}
    
    conn.close()
    return {
        "select_clause": select_clause,
        "base_table": base_table,
        "join_clause": join_clause or "",
        "filter_mappings": filters
    }

def build_query(report_def: dict, ui_filters: Dict[str, Any]) -> str:
    where_conditions = []
    for key, value in ui_filters.items():
        if key in report_def["filter_mappings"]:
            mapping = report_def["filter_mappings"][key]
            column = mapping["column"]
            operator = mapping["op"]

            if isinstance(value, list):
                vals = ", ".join(f"'{v}'" for v in value)
                where_conditions.append(f"{column} IN ({vals})")
            else:
                where_conditions.append(f"{column} {operator} '{value}'")

    where_clause = f"WHERE {' AND '.join(where_conditions)}" if where_conditions else ""

    query = f"""
    SELECT {report_def['select_clause']}
    FROM {report_def['base_table']}
    {report_def['join_clause']}
    {where_clause}
    """.strip()
    return query

@app.get("/run_report/{report_id}")
def run_report(report_id: int, filters: Dict[str, Any] = Query(None)):
    report_def = get_report_definition(report_id)
    if not report_def:
        return {"error": "Report not found"}

    sql_query = build_query(report_def, filters)
    # Here you would execute sql_query on mainframe DB instead of SQLite
    return {"query": sql_query}

@app.post("/add_report")
def add_report(report_name: str, base_table: str, select_clause: str, join_clause: str = ""):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO reports (report_name, base_table, select_clause, join_clause) VALUES (?, ?, ?, ?)",
        (report_name, base_table, select_clause, join_clause)
    )
    conn.commit()
    conn.close()
    return {"status": "Report added"}

@app.post("/add_filter")
def add_filter(report_id: int, ui_filter_key: str, db_column: str, operator: str = "="):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO report_filters (report_id, ui_filter_key, db_column, operator) VALUES (?, ?, ?, ?)",
        (report_id, ui_filter_key, db_column, operator)
    )
    conn.commit()
    conn.close()
    return {"status": "Filter mapping added"}
