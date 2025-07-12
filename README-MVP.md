# ReWear MVP Setup Guide

This guide provides simple instructions to get the ReWear MVP up and running.

## Backend Setup

1. Install Python dependencies:
   ```
   cd backend
   pip install -r requirements.txt
   ```

2. Initialize the database:
   ```
   python init_db.py
   ```

3. Start the FastAPI server:
   ```
   uvicorn app.main:app --reload
   ```

The backend will be available at http://localhost:8000

## Frontend Setup

1. Install Node.js dependencies:
   ```
   npm install
   ```

2. Start the frontend development server:
   ```
   npm run dev
   ```

The frontend will be available at http://localhost:5173

## Demo Login

Use the demo login button on the login page to access the app with the following credentials:
- Email: demo@rewear.com
- Password: demopassword
- Points Balance: 500

## Features Included in MVP

- User authentication (login/register/demo login)
- Browse items
- Item details
- Add new items
- User dashboard
- Points system

## Database

The MVP uses SQLite for simplicity, which requires no additional setup. The database file is created automatically when you run the initialization script.

## API Documentation

FastAPI provides automatic API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
