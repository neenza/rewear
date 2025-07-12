# ReWear - Sustainable Fashion Exchange Platform

ReWear is a web-based platform that enables users to exchange unused clothing through direct swaps or a point-based redemption system. The goal is to promote sustainable fashion and reduce textile waste by encouraging users to reuse wearable garments instead of discarding them.

## Project Overview

### Key Features

- **User Authentication**: Email/password signup and login
- **Item Management**: Upload, browse, and swap clothing items
- **Swap System**: Direct swaps between users or point-based redemptions
- **Admin Moderation**: Review and approve/reject listings
- **Real-time Updates**: Get notified of swap requests and item status changes

### Tech Stack

- **Frontend**: React.js with TypeScript, Material-UI, Redux Toolkit
- **Backend**: FastAPI (Python), PostgreSQL, Redis
- **Storage**: AWS S3 for images
- **Deployment**: Docker, GitHub Actions

## Project Structure

- `/backend` - FastAPI backend API
- `/src` - React frontend application
- `/public` - Static assets
- `/docker-compose.yml` - Docker configuration

## Getting Started

### Prerequisites

- Node.js 18+ and npm/pnpm
- Python 3.7+
- PostgreSQL
- Redis
- Docker (optional)

### Running the Application

#### Development Setup

1. **Clone the repository**:
   ```sh
   git clone https://github.com/neenza/rewear.git
   cd rewear
   ```

2. **Set up the backend**:
   ```sh
   cd backend
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Unix/Mac:
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   # Configure your .env file
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

3. **Set up the frontend**:
   ```sh
   cd ..  # Return to project root
   npm install
   npm run dev
   ```

4. **Access the application**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

#### Using Docker

```sh
docker-compose up -d
## Features in Detail

### User Authentication
- Email/password signup and login
- JWT-based authentication
- Role-based access control (user/admin)
- Profile management

### Item Management
- Image upload with AWS S3 storage
- Detailed item descriptions (category, type, size, condition)
- Tagging system for better discovery
- Approval workflow for quality control

### Swap System
- Direct item-for-item swaps
- Point-based redemptions for asymmetric exchanges
- Swap request and acceptance flow
- Status tracking for all exchanges

### Admin Features
- Moderate and approve/reject item listings
- Remove inappropriate or spam items
- User management
- Platform statistics and reports

## Technologies Used

### Frontend
- **React.js** with TypeScript for type safety
- **Material-UI/Chakra UI** for component library
- **Redux Toolkit** for state management
- **React Hook Form** for form handling
- **React Router** for navigation
- **Axios** for API communication
- **Tailwind CSS** for styling

### Backend
- **FastAPI** for API development
- **PostgreSQL** for data storage
- **SQLAlchemy** for ORM
- **Pydantic** for data validation
- **Redis** for caching
- **JWT** for authentication
- **AWS S3** for file storage
- **Docker** for containerization

## Testing & Quality Assurance
- End-to-end testing with **Cypress**
- Unit testing with **Jest** and **React Testing Library**
- Backend testing with **pytest**
- Code linting with **ESLint** and **Flake8**
- Type checking with TypeScript and Python type hints

## Deployment Options
- Docker Compose for local/development
- AWS/Azure for cloud deployment
- Vercel/Netlify for frontend hosting
- GitHub Actions for CI/CD pipelines
