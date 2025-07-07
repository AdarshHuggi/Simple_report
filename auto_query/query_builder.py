# query_builder.py (modified)
from schema_store import find_relationship
from typing import List, Optional

def build_dynamic_query(fields_used, filters=None, group_by=None, order_by=None, limit=None) -> str:
    filters = filters or []
    group_by = group_by or []
    order_by = order_by or []

    involved_tables = list({f.split(".")[0] for f in fields_used + filters + group_by})
    base_table = involved_tables[0]
    joins = []

    query = f"SELECT {', '.join(fields_used)}\nFROM {base_table}"

    for table in involved_tables[1:]:
        rel = find_relationship(base_table, table)
        if rel:
            joins.append(f"{rel.get_join_type()} {rel.right_table} ON {rel.get_join_condition()}")

    if joins:
        query += "\n" + "\n".join(joins)

    if filters:
        query += "\nWHERE " + " AND ".join(filters)

    if group_by:
        query += "\nGROUP BY " + ", ".join(group_by)

    if order_by:
        order_parts = [f"{item['field']} {item.get('direction', 'ASC')}" for item in order_by]
        query += "\nORDER BY " + ", ".join(order_parts)

    if limit:
        query += f"\nLIMIT {limit}"

    return query

def auto_aggregate_fields(fields: List[str], group_by: List[str]) -> List[str]:
    group_fields = set(group_by)
    result = []
    for field in fields:
        if field not in group_fields:
            alias = field.split(".")[-1]
            result.append(f"SUM({field}) AS {alias}")
        else:
            result.append(field)
    return result
