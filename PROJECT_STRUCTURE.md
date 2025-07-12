# ReWear Project Structure Overview

## Backend (FastAPI)

### Core Components
- `app/main.py` - Main FastAPI application entry point
- `app/core/config.py` - Configuration settings
- `app/core/database.py` - Database connection
- `app/core/security.py` - Authentication and security utilities

### API Components
- `app/api/api.py` - API router configuration
- `app/api/deps.py` - Dependency injection helpers
- `app/api/endpoints/*.py` - API endpoint implementations for different resources

### Data Models
- `app/models/models.py` - SQLAlchemy ORM models for database tables
- `app/schemas/schemas.py` - Pydantic models for validation and serialization

### Services
- `app/services/s3.py` - AWS S3 integration for file storage
- `app/services/redis.py` - Redis caching service

### Database Migrations
- `migrations/env.py` - Alembic migration environment
- `migrations/versions/*.py` - Migration scripts
- `alembic.ini` - Alembic configuration

### Testing
- `tests/conftest.py` - Test fixtures and configuration
- `tests/test_*.py` - Test modules for different components

### Configuration Files
- `.env.example` - Example environment variables
- `.env.test` - Test environment variables
- `Dockerfile` - Docker container configuration
- `Makefile` - Development task automation
- `requirements.txt` - Python dependencies

## Frontend (React/TypeScript)

### Core Components
- `src/main.tsx` - Entry point
- `src/App.tsx` - Main application component
- `src/vite-env.d.ts` - TypeScript declarations for Vite

### Features
- `src/features/auth/*` - Authentication related components
- `src/features/items/*` - Item management components
- `src/features/swaps/*` - Swap system components
- `src/features/admin/*` - Admin panel components

### Common UI
- `src/components/*` - Reusable UI components
- `src/layouts/*` - Page layout components

### State Management
- `src/store/*` - Redux store configuration
- `src/store/slices/*` - Redux slices for different features
- `src/services/api.ts` - API client

### Utilities
- `src/utils/*` - Helper functions
- `src/hooks/*` - Custom React hooks

### Configuration Files
- `tsconfig.json` - TypeScript configuration
- `vite.config.ts` - Vite configuration
- `tailwind.config.ts` - Tailwind CSS configuration
- `postcss.config.js` - PostCSS configuration
- `eslint.config.js` - ESLint configuration

## Project Root
- `docker-compose.yml` - Multi-container Docker configuration
- `README.md` - Project documentation
- `plan.md` - Technical plan and architecture documentation
- `ui_description.md` - UI design documentation
