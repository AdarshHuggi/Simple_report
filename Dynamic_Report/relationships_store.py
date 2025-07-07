

from Dynamic_Report.generate_relationships import generate_relationships_from_db


rels = generate_relationships_from_db()


with open("relationships_store.py", "w") as f:
    f.write("from relationships import TableRelationship\n\n")
    f.write("RELATIONSHIPS = [\n")
    for r in rels:
        f.write(f"    TableRelationship('{r.left_table}', '{r.right_table}', '{r.left_field}', '{r.right_field}', '{r.cardinality}', '{r.integrity}'),\n")
    f.write("]\n")
