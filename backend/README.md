# ReWear Backend API

This is the backend API for the ReWear platform, a web-based application for exchanging unused clothing.

## Features

- User authentication with JWT
- Item management with images
- Swap requests and point-based redemptions
- Admin moderation for listings
- Redis caching for improved performance
- AWS S3 storage for images

## Tech Stack

- FastAPI (Python)
- PostgreSQL
- Redis
- AWS S3
- SQLAlchemy ORM
- Pydantic for validation
- Alembic for migrations

## Development Setup

### Prerequisites

- Python 3.7+
- PostgreSQL
- Redis
- AWS account (for S3) or local alternative

### Setup Steps

1. Clone the repository and navigate to the backend directory:

```bash
cd backend
```

2. Create and activate a virtual environment:

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Unix/Mac
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run database migrations:

```bash
alembic upgrade head
```

6. Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000 with interactive documentation at http://localhost:8000/docs.

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get access token
- `GET /api/auth/me` - Get current user info

### Users

- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile
- `GET /api/users/:id/items` - Get user's items

### Items

- `POST /api/items` - Create new item
- `GET /api/items` - List items with filtering
- `GET /api/items/:id` - Get item details
- `PUT /api/items/:id` - Update item
- `DELETE /api/items/:id` - Delete item

### Swaps

- `POST /api/swaps` - Request a swap
- `GET /api/swaps` - List user's swaps
- `PUT /api/swaps/:id` - Update swap status
- `GET /api/swaps/:id` - Get swap details

### Admin

- `GET /api/admin/items/pending` - List pending items
- `PUT /api/admin/items/:id/approve` - Approve item
- `PUT /api/admin/items/:id/reject` - Reject item

## Docker

You can also run the application using Docker:

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down
```

## Testing

```bash
# Run tests
pytest
```

## Deployment

For production deployment:

1. Update the `.env` file with production settings
2. Use a production-ready database
3. Configure proper CORS settings
4. Set up a reverse proxy (Nginx, etc.)
5. Deploy using Docker or a cloud platform
