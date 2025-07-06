from sql_engine import SQLEngine

if __name__ == "__main__":
    # Example: Use auto_generate to build a query from user-like input
    selected_columns = [
        {"field": "users.id"},
        {"field": "users.name"},
        {"field": "SUM(orders.amount)", "aggregate": True, "alias": "total_amount"}
    ]
    main_table = "users"
    join_info = [
        {"table": "orders", "on": "users.id = orders.user_id", "type": "LEFT"}
    ]
    filters = ["users.active = 1"]
    order_by = [
        {"field": "total_amount", "desc": True}
    ]
    limit = 10

    print("=== auto_generate + print_query ===")
    builder = SQLEngine().auto_generate(
        selected_columns=selected_columns,
        main_table=main_table,
        join_info=join_info,
        filters=filters,
        order_by=order_by,
        limit=limit
    )
    builder.print_query()

    print("\n=== Manual build ===")
    engine = SQLEngine()
    engine.select("id", "users.name", "SUM(orders.amount) AS total_amount")
    engine.from_table("users")
    engine.join("orders", "users.id = orders.user_id", "LEFT")
    engine.where("users.active = 1")
    engine.group_by("users.id", "users.name")
    engine.having("SUM(orders.amount) > 100")
    engine.order_by("total_amount", desc=True)
    engine.limit(5)
    print(engine.build())

    print("\n=== Test print_query ===")
    engine.print_query()

    print("\n=== Test select ===")
    print(engine._select)

    print("\n=== Test from_table ===")
    print(engine._from)

    print("\n=== Test join ===")
    print(engine._joins)

    print("\n=== Test where ===")
    print(engine._where)

    print("\n=== Test group_by ===")
    print(engine._group_by)

    print("\n=== Test having ===")
    print(engine._having)

    print("\n=== Test order_by ===")
    print(engine._order_by)

    print("\n=== Test limit ===")
    print(engine._limit)
