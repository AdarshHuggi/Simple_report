Add new report endpoint input:

{
  "report_name": "sales_summary",
  "base_table": "sales s",
  "select_columns": [
    "s.id AS sale_id",
    "c.name AS customer_name",
    "p.name AS product_name",
    "s.amount",
    "s.date"
  ],
  "joins": [
    "INNER JOIN customers c ON s.customer_id = c.id",
    "INNER JOIN products p ON s.product_id = p.id"
  ],
  "filter_mapping": {
    "customer": "c.name",
    "product": "p.name",
    "min_amount": "s.amount >= {value}",
    "max_amount": "s.amount <= {value}",
    "date_from": "s.date >= '{value}'",
    "date_to": "s.date <= '{value}'"
  },
  "group_by": [
    "c.name",
    "p.name"
  ],
  "order_by": [
    "s.amount DESC"
  ]
}




from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import json

app = FastAPI()

DB_FILE = "reports.db"


def create_tables():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS report_configs (
        report_name TEXT PRIMARY KEY,
        base_table TEXT NOT NULL,
        select_columns TEXT NOT NULL,  -- JSON string
        joins TEXT,                     -- JSON string
        filter_mapping TEXT NOT NULL,   -- JSON string
        group_by TEXT,                  -- JSON string
        order_by TEXT                   -- JSON string
    )
    """)
    
    conn.commit()
    conn.close()
    



class ReportConfig(BaseModel):
    report_name: str
    base_table: str
    select_columns: list
    joins: list = []
    filter_mapping: dict
    group_by: list = []
    order_by: list = []


def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


@app.post("/add_report")
def add_report(config: ReportConfig):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO report_configs
            (report_name, base_table, select_columns, joins, filter_mapping, group_by, order_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            config.report_name,
            config.base_table,
            json.dumps(config.select_columns),
            json.dumps(config.joins),
            json.dumps(config.filter_mapping),
            json.dumps(config.group_by),
            json.dumps(config.order_by)
        ))
        conn.commit()
        return {"message": "Report added/updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@app.get("/list_reports")
def list_reports():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT report_name FROM report_configs")
    reports = [row["report_name"] for row in cursor.fetchall()]
    conn.close()
    return {"reports": reports}


@app.get("/get_report/{report_name}")
def get_report(report_name: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM report_configs WHERE report_name = ?", (report_name,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Report not found")
    return dict(row)

if __name__ == "__main__":
    import uvicorn
    create_tables()
    uvicorn.run(app, host="0.0.0.0", port=8000)
