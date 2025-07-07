import json
from generate_schema_store import generate_schema_from_db

schema = generate_schema_from_db()
with open("schema_store.py", "w") as f:
    f.write("TABLES = ")
    f.write(json.dumps(schema, indent=4))

#