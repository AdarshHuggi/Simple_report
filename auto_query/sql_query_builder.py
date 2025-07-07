
def build_sql_query(config: dict) -> str:
    select_fields = config.get("select", [])
    from_table = config.get("from")
    joins = config.get("joins", [])
    filters = config.get("filters", [])
    group_by = config.get("group_by", [])
    order_by = config.get("order_by", [])
    limit = config.get("limit")

    query_parts = []

    # SELECT
    select_clause = ", ".join(select_fields) if select_fields else "*"
    query_parts.append(f"SELECT {select_clause}")

    # FROM
    query_parts.append(f"FROM {from_table}")

    # JOINS
    for join in joins:
        join_type = join.get("type", "INNER").upper()
        table = join["table"]
        on_clause = join["on"]
        query_parts.append(f"{join_type} JOIN {table} ON {on_clause}")

    # WHERE
    if filters:
        where_clause = " AND ".join(filters)
        query_parts.append(f"WHERE {where_clause}")

    # GROUP BY
    if group_by:
        group_by_clause = ", ".join(group_by)
        query_parts.append(f"GROUP BY {group_by_clause}")

    # ORDER BY
    if order_by:
        order_clause = ", ".join([f"{o['field']} {o.get('direction', 'ASC')}" for o in order_by])
        query_parts.append(f"ORDER BY {order_clause}")

    # LIMIT
    if limit:
        query_parts.append(f"LIMIT {limit}")

    return "\n".join(query_parts)
