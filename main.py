from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database.db import create_tables_and_insert_data
from app.routers.report import report_router

app = FastAPI()

# Mount static directory for CSS/JS
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(report_router)

@app.get("/", response_class=FileResponse)
def serve_index():
    return "static/index.html"

if __name__ == "__main__":
    import uvicorn
    create_tables_and_insert_data()
    uvicorn.run(app, host="0.0.0.0", port=8080)