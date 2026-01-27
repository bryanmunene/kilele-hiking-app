# Kilele Hiking API - Backend

Python FastAPI backend for the Kilele hiking trails application.

## Setup

### 1. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
```bash
# Copy example env file
copy .env.example .env

# Edit .env with your settings
```

### 4. Seed Database
```bash
python seed_data.py
```

### 5. Run Development Server
```bash
# Option 1: Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using Python
python main.py
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Hikes
- `GET /api/v1/hikes` - List all hikes (with optional filters)
- `GET /api/v1/hikes/{id}` - Get specific hike
- `POST /api/v1/hikes` - Create new hike
- `PUT /api/v1/hikes/{id}` - Update hike
- `DELETE /api/v1/hikes/{id}` - Delete hike

### Query Parameters
- `?difficulty=Moderate` - Filter by difficulty (Easy, Moderate, Hard, Extreme)
- `?skip=0&limit=100` - Pagination

## Project Structure
```
backend/
├── main.py              # FastAPI app entry point
├── database.py          # SQLAlchemy database configuration
├── requirements.txt     # Python dependencies
├── seed_data.py         # Database seeding script
├── .env.example         # Environment template
├── models/              # SQLAlchemy models
│   ├── __init__.py
│   └── hike.py
├── schemas/             # Pydantic schemas for validation
│   ├── __init__.py
│   └── hike.py
└── routers/             # API route handlers
    ├── __init__.py
    └── hikes.py
```

## Database

Using SQLite for development (easy to migrate to PostgreSQL/MySQL for production).

### Schema: Hikes Table
- `id` - Integer (Primary Key)
- `name` - String(200)
- `location` - String(200)
- `difficulty` - String(50): Easy, Moderate, Hard, Extreme
- `distance_km` - Float
- `elevation_gain_m` - Float
- `estimated_duration_hours` - Float
- `description` - Text
- `trail_type` - String(100): Loop, Out and Back, Point to Point
- `best_season` - String(200)
- `latitude` - Float
- `longitude` - Float
- `image_url` - String(500)
- `created_at` - DateTime
- `updated_at` - DateTime

## Development

### Running Tests
```bash
pytest
```

### Database Migrations (Future)
Consider adding Alembic for migrations:
```bash
pip install alembic
alembic init migrations
```

## Production Deployment

### Environment Variables
Set these in production:
- `DATABASE_URL` - PostgreSQL connection string
- `API_HOST` - 0.0.0.0
- `API_PORT` - 8000
- `DEBUG` - False

### Using PostgreSQL
```bash
# Install PostgreSQL driver
pip install psycopg2-binary

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://user:password@localhost:5432/kilele_db
```

### Deploy Options
- **Railway**: `railway up`
- **Render**: Connect GitHub repo
- **Heroku**: `heroku create && git push heroku main`
- **DigitalOcean App Platform**: Connect GitHub repo
