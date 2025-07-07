""" schema_store.py"""
# In schema_store.py
import json
from relationships import TableRelationship

with open("schema_store.json") as f:
    TABLES = json.load(f)


def get_all_tables():
    return list(TABLES.keys())

def get_table_fields(table: str):
    return TABLES[table]["fields"].keys()

def get_field_type(table: str, field: str):
    return TABLES[table]["fields"].get(field)

def get_all_fields():
    # Returns flat list like ["Orders.OrderID", "Customers.CustomerName"]
    fields = []
    for table, meta in TABLES.items():
        for field in meta["fields"]:
            fields.append(f"{table}.{field}")
    return fields

def find_relationship(left_table, right_table):
    for rel in RELATIONSHIPS:
        if rel.left_table == left_table and rel.right_table == right_table:
            return rel
    return None
