# schema_store.py
from relationships import TableRelationship

TABLES = {
    "Orders": ["OrderID", "CustomerID", "Amount", "Region"],
    "Customers": ["ID", "CustomerName", "Country"]
}

RELATIONSHIPS = [
    TableRelationship("Orders", "Customers", "CustomerID", "ID")
]

def find_relationship(left_table, right_table):
    for r in RELATIONSHIPS:
        if r.left_table == left_table and r.right_table == right_table:
            return r
    return None
