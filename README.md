# Report Generation FastAPI Application

This project is a FastAPI-based report generation application using SQLite3 as the database. It features a modular structure with routers, models, schemas, and database logic separated for maintainability.

## Features

- User, report, and report data tables
- Sample data inserted on startup
- Endpoints to fetch users, reports, and report data

## Getting Started

1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Run the application:
   ```sh
   uvicorn main:app --reload
   ```
3. Access the API docs at [http://localhost:8000/docs](http://localhost:8000/docs)

## Project Structure

- `main.py`: FastAPI app entry point
- `app/database/db.py`: Database connection and setup
- `app/routers/`: API route definitions
- `app/models/`: Data transformation helpers
- `app/schemas/`: Pydantic models

---

This project is ready for further extension and customization for your reporting needs.
