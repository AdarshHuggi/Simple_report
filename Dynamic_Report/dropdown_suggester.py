# dropdown_suggester.py
from schema_store import TABLES
from relationships_store import RELATIONSHIPS

def get_related_tables(base_table):
    related = set()
    for r in RELATIONSHIPS:
        if r.left_table == base_table:
            related.add(r.right_table)
        elif r.right_table == base_table:
            related.add(r.left_table)
    return list(related)

def get_dropdown_options(base_table):
    options = list(TABLES[base_table]["fields"].keys())
    related_tables = get_related_tables(base_table)
    for t in related_tables:
        options += [f"{t}.{f}" for f in TABLES[t]["fields"].keys()]
    return options
