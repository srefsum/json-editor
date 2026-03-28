# JSON Editor

A full-stack web application for creating, editing, and managing JSON documents and JSON schemas.

## Features

- 📝 Create, read, update, and delete JSON documents
- 🔍 Create and manage JSON schemas
- ✅ Validate JSON documents against schemas
- 🎨 Modern Vue.js frontend with syntax highlighting
- 🚀 Fast API backend with Python FastAPI
- 💾 PostgreSQL database for persistent storage

## Architecture

- **Frontend**: Vue 3 with Composition API, Vite, Tailwind CSS
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy
- **Database**: PostgreSQL 14+

## Project Structure

```
json-editor/
├── backend/          # FastAPI backend application
│   ├── src/
│   │   ├── routes/   # API endpoints
│   │   ├── models/   # Database models
│   │   ├── controllers/  # Business logic
│   │   └── db/       # Database configuration
│   └── migrations/   # Database migrations
├── frontend/         # Vue.js frontend application
│   └── src/
│       ├── components/
│       ├── views/
│       └── services/
└── docker-compose.yml
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Docker (optional)

## Quick Start

### Using Docker Compose (Recommended)

```bash
docker-compose up -d
```

### Manual Setup

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

#### Database

```bash
# Create database
createdb json_editor

# Run migrations
cd backend
alembic upgrade head
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

### Backend
- API runs on http://localhost:8000
- Auto-reload enabled in development mode

### Frontend
- Dev server runs on http://localhost:5173
- Hot module replacement enabled

## License

MIT
