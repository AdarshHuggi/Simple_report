class SQLEngine:
    """
    Dynamic SQL query builder for reporting, similar to Tableau or BI tools.
    Supports flexible clause addition and safe query generation.
    """
    def __init__(self):
        self._select = []
        self._from = None
        self._joins = []
        self._where = []
        self._group_by = []
        self._having = []
        self._order_by = []
        self._limit = None

    def select(self, *columns):
        for col in columns:
            if isinstance(col, (list, tuple)):
                self._select.extend([c for c in col if isinstance(c, str) and c.strip()])
            elif isinstance(col, str) and col.strip():
                self._select.append(col)
            else:
                raise ValueError(f"Invalid column in SELECT: {col}")
        return self

    def from_table(self, table):
        if not isinstance(table, str) or not table.strip():
            raise ValueError("FROM table must be a non-empty string.")
        self._from = table.strip()
        return self

    def join(self, table, on, join_type="INNER"):
        if not isinstance(table, str) or not table.strip():
            raise ValueError("JOIN table must be a non-empty string.")
        if not isinstance(on, str) or not on.strip():
            raise ValueError("JOIN ON condition must be a non-empty string.")
        join_type = join_type.upper()
        if join_type not in ["INNER", "LEFT", "RIGHT", "FULL", "CROSS"]:
            raise ValueError("Invalid join type.")
        self._joins.append(f"{join_type} JOIN {table.strip()} ON {on.strip()}")
        return self

    def where(self, condition):
        if not isinstance(condition, str) or not condition.strip():
            raise ValueError("WHERE condition must be a non-empty string.")
        self._where.append(condition.strip())
        return self

    def group_by(self, *columns):
        for col in columns:
            if isinstance(col, (list, tuple)):
                self._group_by.extend([c for c in col if isinstance(c, str) and c.strip()])
            elif isinstance(col, str) and col.strip():
                self._group_by.append(col)
            else:
                raise ValueError(f"Invalid column in GROUP BY: {col}")
        return self

    def having(self, condition):
        if not isinstance(condition, str) or not condition.strip():
            raise ValueError("HAVING condition must be a non-empty string.")
        self._having.append(condition.strip())
        return self

    def order_by(self, column, desc=False):
        if not isinstance(column, str) or not column.strip():
            raise ValueError("ORDER BY column must be a non-empty string.")
        order = "DESC" if desc else "ASC"
        self._order_by.append(f"{column.strip()} {order}")
        return self

    def limit(self, count):
        if not isinstance(count, int) or count < 1:
            raise ValueError("LIMIT must be a positive integer.")
        self._limit = count
        return self

    def build(self):
        if not self._select:
            raise ValueError("SELECT clause is required.")
        if not self._from:
            raise ValueError("FROM clause is required.")
        query = [
            f"SELECT {', '.join(self._select)}",
            f"FROM {self._from}"
        ]
        if self._joins:
            query.extend(self._joins)
        if self._where:
            query.append(f"WHERE {' AND '.join(self._where)}")
        if self._group_by:
            query.append(f"GROUP BY {', '.join(self._group_by)}")
        if self._having:
            query.append(f"HAVING {' AND '.join(self._having)}")
        if self._order_by:
            query.append(f"ORDER BY {', '.join(self._order_by)}")
        if self._limit:
            query.append(f"LIMIT {self._limit}")
        return " ".join(query)

    def print_query(self):
        print(self.build())

    def auto_generate(self, selected_columns, main_table, join_info=None, filters=None, order_by=None, limit=None):
        """
        selected_columns: list of dicts, e.g. [{"field": "users.name"}, {"field": "SUM(orders.amount)", "aggregate": True, "alias": "total_amount"}]
        main_table: str, the main table name
        join_info: list of dicts, e.g. [{"table": "orders", "on": "users.id = orders.user_id", "type": "LEFT"}]
        filters: list of str, WHERE conditions
        order_by: list of dicts, e.g. [{"field": "total_amount", "desc": True}]
        limit: int
        """
        self._select = []
        self._group_by = []
        self._having = []
        has_aggregate = False
        for col in selected_columns:
            if isinstance(col, dict):
                field = col.get("field")
                alias = col.get("alias")
                aggregate = col.get("aggregate", False)
                if aggregate:
                    has_aggregate = True
                select_expr = field
                if alias:
                    select_expr += f" AS {alias}"
                self._select.append(select_expr)
                if not aggregate:
                    self._group_by.append(field)
            elif isinstance(col, str):
                self._select.append(col)
                self._group_by.append(col)
            else:
                raise ValueError(f"Invalid column: {col}")
        self._from = main_table
        self._joins = []
        if join_info:
            for join in join_info:
                table = join.get("table")
                on = join.get("on")
                join_type = join.get("type", "INNER")
                if not table or not on:
                    raise ValueError("Join table and ON condition are required. Please provide join details.")
                self.join(table, on, join_type)
        self._where = filters if filters else []
        self._order_by = []
        if order_by:
            for ob in order_by:
                field = ob.get("field")
                desc = ob.get("desc", False)
                self.order_by(field, desc)
        self._limit = limit
        return self
