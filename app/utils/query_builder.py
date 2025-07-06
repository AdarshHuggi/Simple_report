class SQLQueryBuilder:
    def __init__(self, base_table):
        self.base_table = base_table
        self.joins = []            # List of join clauses
        self.select_fields = []    # Fields to select
        self.aggregations = {}     # { field_name: aggregation_type }
        self.filters = []          # Non-aggregated filters -> WHERE
        self.having_filters = []   # Aggregated filters -> HAVING
        self.order_by = []         # (field, ASC/DESC)

    def add_join(self, join_type, table, on_condition):
        self.joins.append(f"{join_type.upper()} JOIN {table} ON {on_condition}")

    def add_field(self, field_name, is_aggregate=False, agg_func=None):
        if is_aggregate:
            self.aggregations[field_name] = agg_func.upper()
        else:
            self.select_fields.append(field_name)

    def add_filter(self, condition, is_aggregate=False):
        if is_aggregate:
            self.having_filters.append(condition)
        else:
            self.filters.append(condition)

    def add_order_by(self, field, direction="ASC"):
        self.order_by.append(f"{field} {direction.upper()}")

    def build_query(self):
        select_parts = self.select_fields.copy()
        for field, agg in self.aggregations.items():
            select_parts.append(f"{agg}({field}) AS {agg.lower()}_{field}")

        query = f"SELECT {', '.join(select_parts)}\nFROM {self.base_table}"

        if self.joins:
            query += "\n" + "\n".join(self.joins)

        if self.filters:
            query += "\nWHERE " + " AND ".join(self.filters)

        if self.aggregations:
            group_by = ", ".join(self.select_fields)
            if group_by:
                query += f"\nGROUP BY {group_by}"

        if self.having_filters:
            query += "\nHAVING " + " AND ".join(self.having_filters)

        if self.order_by:
            query += "\nORDER BY " + ", ".join(self.order_by)

        return query + ";"


query_builder = SQLQueryBuilder(base_table="Orders")

# Join Customers table
query_builder.add_join("INNER", "Customers", "Orders.CustomerID = Customers.CustomerID")

# Add dimensions
query_builder.add_field("Region")          # Non-aggregated
query_builder.add_field("Customers.Name")  # Non-aggregated

# Add measures
query_builder.add_field("Sales", is_aggregate=True, agg_func="SUM")
query_builder.add_field("Profit", is_aggregate=True, agg_func="AVG")

# Add filters
query_builder.add_filter("OrderDate >= '2023-01-01'")
query_builder.add_filter("Region = 'West'")

# Add aggregated filter (like HAVING clause)
query_builder.add_filter("SUM(Sales) > 1000", is_aggregate=True)

# Add order by
query_builder.add_order_by("SUM(Sales)", "DESC")

# Generate SQL
sql = query_builder.build_query()
print(sql)
