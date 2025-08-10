from typing import Dict, List, Any

# -----------------------------------------
# Report configurations (predefined SELECT, JOINs, mappings)
# -----------------------------------------
REPORT_CONFIGS = {
    "sales_report": {
        "base_table": "sales s",
        "select": [
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
        }
    },
    "inventory_report": {
        "base_table": "inventory i",
        "select": [
            "i.id AS inventory_id",
            "p.name AS product_name",
            "i.stock_quantity",
            "i.last_updated"
        ],
        "joins": [
            "INNER JOIN products p ON i.product_id = p.id"
        ],
        "filter_mapping": {
            "product": "p.name",
            "min_stock": "i.stock_quantity >= {value}",
            "max_stock": "i.stock_quantity <= {value}",
            "updated_after": "i.last_updated >= '{value}'"
        }
    }
}


# -----------------------------------------
# SQL Builder Class
# -----------------------------------------
class ReportQueryBuilder:
    def __init__(self, report_name: str):
        if report_name not in REPORT_CONFIGS:
            raise ValueError(f"Unknown report: {report_name}")
        self.config = REPORT_CONFIGS[report_name]
        self.filters = []

    def apply_filters(self, user_filters: Dict[str, Any]):
        mapping = self.config["filter_mapping"]
        for key, val in user_filters.items():
            if key in mapping and val is not None and val != "":
                condition_template = mapping[key]
                # If template has {value}, format it
                if "{value}" in condition_template:
                    condition = condition_template.format(value=val)
                else:
                    # Default equality condition
                    condition = f"{mapping[key]} = '{val}'"
                self.filters.append(condition)

    def build_query(self) -> str:
        select_clause = ", ".join(self.config["select"])
        query = f"SELECT {select_clause} FROM {self.config['base_table']}"
        
        if self.config.get("joins"):
            query += " " + " ".join(self.config["joins"])
        
        if self.filters:
            query += " WHERE " + " AND ".join(self.filters)

        return query + ";"


# -----------------------------------------
# Example Usage
# -----------------------------------------
# Simulated UI input for sales report
ui_filters_sales = {
    "customer": "John Doe",
    "min_amount": 500,
    "max_amount": 2000,
    "date_from": "2025-01-01",
    "date_to": "2025-01-31"
}

# Build sales report query
builder_sales = ReportQueryBuilder("sales_report")
builder_sales.apply_filters(ui_filters_sales)
sales_query = builder_sales.build_query()

print("Sales Report Query:")
print(sales_query)


# Simulated UI input for inventory report
ui_filters_inventory = {
    "product": "Laptop",
    "min_stock": 10,
    "updated_after": "2025-08-01"
}

# Build inventory report query
builder_inventory = ReportQueryBuilder("inventory_report")
builder_inventory.apply_filters(ui_filters_inventory)
inventory_query = builder_inventory.build_query()

print("\nInventory Report Query:")
print(inventory_query)
