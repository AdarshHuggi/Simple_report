# export_to_twb.py
import xml.etree.ElementTree as ET
from generate_relationships import generate_relationships_from_db
from generate_schema_store import generate_schema_from_db

def export_to_twb(filename="output.twb"):
    root = ET.Element("datasource")

    schema = generate_schema_from_db()
    for table, meta in schema.items():
        table_el = ET.SubElement(root, "table", name=table)
        for col, col_type in meta["fields"].items():
            ET.SubElement(table_el, "column", name=col, datatype=col_type)

    for rel in generate_relationships_from_db():
        ET.SubElement(root, "relation", 
                      left=rel.left_table, 
                      right=rel.right_table,
                      left_key=rel.left_field,
                      right_key=rel.right_field,
                      join_type=rel.get_join_type())

    tree = ET.ElementTree(root)
    tree.write(filename, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    export_to_twb()
