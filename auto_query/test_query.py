# test_query.py

from query_builder import build_dynamic_query

fields = [
    "Orders.OrderID",
    "Customers.CustomerName",
    "Orders.Amount"
]

query = build_dynamic_query(fields)
print(query)
