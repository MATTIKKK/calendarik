# Calendarik Backend

This is the FastAPI backend for the Calendarik application.

## Setup

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file with the following variables:

```
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/calendarik

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Frontend URL
FRONTEND_URL=http://localhost:5173
```

4. Create the database:

```bash
# Install PostgreSQL if not already installed
# Create a new database named 'calendarik'
createdb calendarik
```

5. Run migrations:

```bash
alembic upgrade head
```

6. Start the server:

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

Once the server is running, you can access:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
