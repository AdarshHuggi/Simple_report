# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from query_builder import build_dynamic_query
import sqlite3

app = FastAPI()

# main.py (modified)
from typing import List, Optional

class FieldRequest(BaseModel):
    fields: List[str]
    filters: Optional[List[str]] = []
    group_by: Optional[List[str]] = []
    order_by: Optional[List[dict]] = []  # e.g., [{"field": "TotalAmount", "direction": "DESC"}]
    limit: Optional[int] = None


@app.post("/generate_sql/")
def generate_sql(req: FieldRequest):
    sql = build_dynamic_query(req.fields, req.filters, req.group_by)
    return {"sql": sql}

@app.post("/run_query/")
def run_query(req: FieldRequest):
    sql = build_dynamic_query(req.fields, req.filters, req.group_by)
    conn = sqlite3.connect("tableau_sim.db")
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    conn.close()
    return {"sql": sql, "data": [dict(zip(columns, row)) for row in rows]}




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)