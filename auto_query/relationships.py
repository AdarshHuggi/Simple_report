# relationships.py
class TableRelationship:
    def __init__(self, left_table, right_table, left_field, right_field,
                 cardinality="many-to-one", integrity="all-matching"):
        self.left_table = left_table
        self.right_table = right_table
        self.left_field = left_field
        self.right_field = right_field
        self.cardinality = cardinality
        self.integrity = integrity

    def get_join_condition(self):
        return f"{self.left_table}.{self.left_field} = {self.right_table}.{self.right_field}"

    def get_join_type(self):
        return "LEFT JOIN" if self.integrity == "all-matching" else "INNER JOIN"
