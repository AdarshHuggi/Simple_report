from fastapi import APIRouter, Query, Body, HTTPException
from typing import List, Dict
from app.database.db import get_connection
from app.models import models
from app.schemas import schemas
from app.utils.query_builder import SQLQueryBuilder

report_router = APIRouter(prefix="/reports", tags=["reports"])

@report_router.get("/users", response_model=list[schemas.User])
def get_users():
    conn = get_connection()
    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    return [models.user_from_row(row) for row in users]

@report_router.get("/", response_model=dict)
def index():
    return {"welcome": "to the report_app"}

@report_router.get("/data", response_model=list[schemas.ReportData])
def get_report_data():
    conn = get_connection()
    data = conn.execute("SELECT * FROM report_data").fetchall()
    conn.close()
    return [models.report_data_from_row(row) for row in data]

@report_router.get("/tables", response_model=List[str])
def get_tables():
    """
    Get all table names in the database.
    """
    conn = get_connection()
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

@report_router.get("/columns", response_model=Dict[str, List[str]])
def get_columns(table_names: List[str] = Query(..., description="List of table names")):
    """
    Get column names for the given list of tables.
    """
    conn = get_connection()
    result = {}
    for table in table_names:
        cursor = conn.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        result[table] = columns
    conn.close()
    return result

@report_router.post("/generate_query")
def generate_query(payload: dict = Body(...)):
    """
    Generate SQL query based on user selections.
    Expects payload:
    {
        "base_table": str,
        "fields": [str],  # e.g. ["table1.col1", "table2.col2"]
        "joins": [
            {
                "join_type": "INNER"|"LEFT"|"RIGHT",
                "table": str,
                "on_condition": str
            }
        ],
        "filters": [str],      # WHERE conditions
        "having": [str],       # HAVING conditions
        "order_by": [ [str, str] ],  # [field, direction]
        "group_by": [str]      # GROUP BY fields (optional)
    }
    """
    qb = SQLQueryBuilder(base_table=payload["base_table"])
    for field in payload.get("fields", []):
        qb.add_field(field)
    for join in payload.get("joins", []):
        qb.add_join(join["join_type"], join["table"], join["on_condition"])
    for f in payload.get("filters", []):
        qb.add_filter(f)
    for h in payload.get("having", []):
        qb.add_filter(h, is_aggregate=True)
    for ob in payload.get("order_by", []):
        qb.add_order_by(ob[0], ob[1])
    # Add group by if present
    if "group_by" in payload and payload["group_by"]:
        qb.set_group_by(payload["group_by"])
    sql = qb.build_query()
    return {"query": sql}

@report_router.post("/execute_query")
def execute_query(payload: dict = Body(...)):
    """
    Execute a SQL query and return the result as JSON.
    Expects payload:
    {
        "query": str
    }
    Returns:
    {
        "columns": [str],
        "rows": [ [value, ...], ... ]
    }
    """
    sql = payload.get("query")
    if not sql:
        raise HTTPException(status_code=400, detail="No query provided")
    conn = get_connection()
    try:
        cursor = conn.execute(sql)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        data = [list(row) for row in rows]
        return {"columns": columns, "rows": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

