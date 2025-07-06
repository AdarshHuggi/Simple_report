from pydantic import BaseModel

class User(BaseModel):
    id: int
    username: str
    email: str

class Report(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: str

class ReportData(BaseModel):
    id: int
    report_id: int
    data: str
