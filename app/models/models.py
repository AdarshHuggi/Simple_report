from sqlite3 import Row

def user_from_row(row: Row):
    return {
        "id": row["id"],
        "username": row["username"],
        "email": row["email"]
    }

def report_from_row(row: Row):
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "title": row["title"],
        "created_at": row["created_at"]
    }

def report_data_from_row(row: Row):
    return {
        "id": row["id"],
        "report_id": row["report_id"],
        "data": row["data"]
    }
