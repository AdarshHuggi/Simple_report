class SQLQueryBuilder:
    def __init__(self, base_table):
        self.base_table = base_table
        self.select_clauses = []
        self.joins = []
        self.where_conditions = []
        self.group_by_fields = []
        self.having_conditions = []
        self.order_by_fields = []
        self.limit_count = None

    def add_select(self, column, alias=None, aggregate=None, case_when=None, window=None):
        if case_when:
            case_str = "CASE "
            for condition, value in case_when["conditions"]:
                case_str += f"WHEN {condition} THEN {value} "
            case_str += f"ELSE {case_when.get('else', 'NULL')} END"
            if alias:
                case_str += f" AS {alias}"
            self.select_clauses.append(case_str)
        elif aggregate:
            agg_str = f"{aggregate}({column})"
            if window:
                agg_str += f" OVER ({window})"
            if alias:
                agg_str += f" AS {alias}"
            self.select_clauses.append(agg_str)
        else:
            col_str = f"{column}"
            if alias:
                col_str += f" AS {alias}"
            self.select_clauses.append(col_str)

    def add_join(self, join_type, table, condition):
        self.joins.append(f"{join_type.upper()} JOIN {table} ON {condition}")

    def add_where(self, condition):
        self.where_conditions.append(condition)

    def add_group_by(self, field):
        self.group_by_fields.append(field)

    def add_having(self, condition):
        self.having_conditions.append(condition)

    def add_order_by(self, field, direction="ASC"):
        self.order_by_fields.append(f"{field} {direction}")

    def set_limit(self, limit):
        self.limit_count = limit

    def build(self):
        query = f"SELECT {', '.join(self.select_clauses) if self.select_clauses else '*'} FROM {self.base_table}"

        if self.joins:
            query += " " + " ".join(self.joins)

        if self.where_conditions:
            query += " WHERE " + " AND ".join(self.where_conditions)

        if self.group_by_fields:
            query += " GROUP BY " + ", ".join(self.group_by_fields)

        if self.having_conditions:
            query += " HAVING " + " AND ".join(self.having_conditions)

        if self.order_by_fields:
            query += " ORDER BY " + ", ".join(self.order_by_fields)

        if self.limit_count is not None:
            query += f" LIMIT {self.limit_count}"

        return query + ";"


# ------------------- Example Usage -------------------
builder = SQLQueryBuilder("sales")

# SELECT with aggregate and alias
builder.add_select("region", alias="sales_region")
builder.add_select("amount", aggregate="SUM", alias="total_sales")
builder.add_select("amount", aggregate="AVG", alias="avg_sales", window="PARTITION BY region")

# CASE example
builder.add_select(None, alias="sales_category", case_when={
    "conditions": [
        ("amount > 1000", "'High'"),
        ("amount BETWEEN 500 AND 1000", "'Medium'")
    ],
    "else": "'Low'"
})

# JOIN example
builder.add_join("LEFT", "customers", "sales.customer_id = customers.id")

# WHERE
builder.add_where("sales.date >= '2025-01-01'")
builder.add_where("sales.date <= '2025-01-31'")

# GROUP BY / HAVING
builder.add_group_by("region")
builder.add_having("SUM(amount) > 10000")

# ORDER BY
builder.add_order_by("total_sales", "DESC")

# LIMIT
builder.set_limit(10)

# Build SQL
sql_query = builder.build()
print(sql_query)
#==================================================================================
SELECT region AS sales_region,
       SUM(amount) AS total_sales,
       AVG(amount) OVER (PARTITION BY region) AS avg_sales,
       CASE WHEN amount > 1000 THEN 'High'
            WHEN amount BETWEEN 500 AND 1000 THEN 'Medium'
            ELSE 'Low' END AS sales_category
FROM sales
LEFT JOIN customers ON sales.customer_id = customers.id
WHERE sales.date >= '2025-01-01' AND sales.date <= '2025-01-31'
GROUP BY region
HAVING SUM(amount) > 10000
ORDER BY total_sales DESC
LIMIT 10;
