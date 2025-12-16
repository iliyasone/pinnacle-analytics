# Pinnacle Analytics API

A FastAPI-based REST API for accessing Pinnacle betting data. This API provides endpoints to retrieve betting history and client balance information, secured with API key authentication.

## Features

- **Get Bets**: Retrieve settled bets for a specified time period (up to 30 days)
- **Get Client Balance**: Retrieve current client balance
- **Header-Based Authentication**: Secure access using API keys via `X-Api-Key` header
- **API Key Management**: Create, list, activate, deactivate, and delete API keys
- **Tracking**: API keys include created_at timestamps and is_active status
- **Docker Support**: Easy deployment with Docker Compose
- **CORS Enabled**: Compatible with Google Apps Script and other web clients

## Prerequisites

- Python 3.13+
- Docker and Docker Compose (for containerized deployment)
- PostgreSQL (included in Docker Compose setup)
- Pinnacle API credentials

## Set up

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Test

```bash
uv run python tests/scipts/check_get_bets.py 
```

## Quick Start with Docker

1. Clone the repository and navigate to the project directory

2. Copy the example environment file and configure it:
```bash
cp .env.example .env
```

3. Edit `.env` and add your Pinnacle API credentials:
```
PS3838_LOGIN=
PS3838_PASSWORD=
PS3838_API_BASE_URL=
```

4. Start the services:
```bash
docker-compose up -d
```

5. The API will be available at `http://localhost:8000`

## Local Development Setup

1. Install dependencies using uv:
```bash
uv sync
```

2. Set up your environment variables in `.env`
   - For local development, you can use SQLite: `DATABASE_URL=sqlite:///./pinnacle_analytics.db`
   - For production, use PostgreSQL (see `.env.example`)

3. Start the development server:
```bash
uv run uvicorn app.main:app --reload
```

Note: Database migrations run automatically on application startup. Tables will be initialized if the database is empty.

## API Key Management

### Add a new API key (auto-generated):
```bash
uv run python manage_api_keys.py add
```

### Add a specific API key:
```bash
uv run python manage_api_keys.py add your-custom-key-here
```

### List all API keys:
```bash
uv run python manage_api_keys.py list
```

### Activate an API key:
```bash
uv run python manage_api_keys.py activate <key>
```

### Deactivate an API key:
```bash
uv run python manage_api_keys.py deactivate <key>
```

### Delete an API key:
```bash
uv run python manage_api_keys.py delete <key>
```

## API Endpoints

All endpoints require authentication via the `X-Api-Key` header.

### 1. Get Bets

Retrieve settled bets for a specified time period.

**Endpoint:** `POST /get_bets`

**Headers:**
- `X-Api-Key`: Your API key for authentication

**Request Body:**
```json
{
  "days": 7
}
```

**Parameters:**
- `days` (integer, optional): Number of past days to retrieve bets (1-30, default: 1)

**Response:**
```json
{
  "data": {
    // Pinnacle API bet data
  }
}
```

### 2. Get Client Balance

Retrieve the current client balance.

**Endpoint:** `POST /get_client_balance`

**Headers:**
- `X-Api-Key`: Your API key for authentication

**Request Body:**
```json
{}
```

**Response:**
```json
{
  "data": {
    // Pinnacle API balance data
  }
}
```

### 3. Health Check

Check if the API is running.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy"
}
```

## Google Apps Script Example

```javascript
function getPinnacleData() {
  const API_KEY = "your-api-key-here";
  const API_URL = "http://your-server:8000";

  // Get bets for the last 7 days
  const betsResponse = UrlFetchApp.fetch(API_URL + "/get_bets", {
    method: "POST",
    contentType: "application/json",
    headers: {
      "X-Api-Key": API_KEY
    },
    payload: JSON.stringify({
      days: 7
    })
  });

  const betsData = JSON.parse(betsResponse.getContentText());
  Logger.log(betsData);

  // Get client balance
  const balanceResponse = UrlFetchApp.fetch(API_URL + "/get_client_balance", {
    method: "POST",
    contentType: "application/json",
    headers: {
      "X-Api-Key": API_KEY
    },
    payload: JSON.stringify({})
  });

  const balanceData = JSON.parse(balanceResponse.getContentText());
  Logger.log(balanceData);
}
```

## Database Migrations

Migrations run automatically on application startup, initializing tables for empty databases or applying pending migrations for existing databases.

### Create a new migration:
```bash
uv run alembic revision --autogenerate -m "description"
```

### Manually apply migrations (optional):
```bash
uv run alembic upgrade head
```

### Rollback one migration:
```bash
uv run alembic downgrade -1
```

## Development

### Run linters:
```bash
uv run pyright
uv run ruff check
uv run ruff format
```

## Project Structure

```
pinnacle-analytics/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py       # API endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py       # Application configuration
│   │   └── security.py     # Authentication and security
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py     # Database connection and session
│   │   └── models.py       # SQLAlchemy models
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── requests.py     # Request schemas
│   │   └── responses.py    # Response schemas
│   ├── __init__.py
│   └── main.py            # FastAPI application
├── alembic/
│   ├── versions/          # Database migrations
│   └── env.py            # Alembic configuration
├── manage_api_keys.py     # API key management utility
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile            # Docker image configuration
├── pyproject.toml        # Python dependencies
├── .env.example          # Example environment variables
└── README.md            # This file
```

## Security Notes

- API keys are stored securely in PostgreSQL
- CORS is configured to accept all origins for Google Apps Script compatibility
- Never commit your `.env` file or API keys to version control
- Use strong, randomly generated API keys in production

## Troubleshooting

### Database connection errors
- Ensure PostgreSQL is running and accessible
- Check your `DATABASE_URL` in `.env`
- Verify database credentials

### API key authentication errors
- Ensure you've added at least one API key using `manage_api_keys.py`
- Verify the API key is correct in your requests

### Docker issues
- Run `docker-compose logs api` to view API logs
- Run `docker-compose logs db` to view database logs
- Ensure ports 8000 and 5432 are not already in use