# Oil API

A FastAPI application for managing oil resource data with PostgreSQL integration.

## Features

- Create oil resources with date and price information
- Retrieve oil resources by ID
- List all oil resources
- Async database operations with PostgreSQL
- Data validation and error handling

## Requirements

- Python 3.9+
- Poetry (for dependency management)
- PostgreSQL database (Supabase provided)

## Setup

1. Clone the repository

2. Install dependencies

```bash
poetry install
```

3. Configure environment variables

Copy the `.env.example` file to `.env` and update it with your actual configuration values:

```bash
cp .env.example .env
```

Then edit the `.env` file with your actual database credentials and other settings. This is crucial for both the application and database migrations to work properly.

### Security Environment Variables

The application uses the following environment variables for security settings:

- CONFIGURE JWKS_URI: The URL for the JSON Web Key Set (JWKS) from your authentication server. This is used to validate JWT tokens.

**Important Security Note:**
- Never commit your `.env` file with real credentials to version control. The `.env` file is already in `.gitignore` to prevent accidental commits.
- In production environments, always set the security-related variables to "true" when using HTTPS.

4. Run database migrations

```bash
poetry run alembic upgrade head
```

5. Start the application

```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Documentation

After starting the application, you can access:

- Interactive API documentation: http://localhost:8000/api/v1/docs
- ReDoc API documentation: http://localhost:8000/api/v1/redoc

### Create an Oil Resource

```bash
curl -X POST http://localhost:8000/api/v1/oil/ \
  -H "Content-Type: application/json" \
  -d '{"date": "2023-11-22", "price": 75.43}'
```

### Get All Oil Resources

```bash
curl -X GET http://localhost:8000/api/v1/oil/
```

### Get a Specific Oil Resource

```bash
curl -X GET http://localhost:8000/api/v1/oil/1
```

## Database Migrations

Before running the application for the first time, make sure to run the database migrations:

```bash
poetry run alembic upgrade head
```

To create new migrations after modifying models:

```bash
poetry run alembic revision --autogenerate -m "describe your changes"
```

**Note:** Alembic uses the `DATABASE_URI` from your `.env` file for migrations. Make sure this is properly configured before running any migration commands.
