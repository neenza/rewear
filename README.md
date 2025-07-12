##Problem Statement: ReWear – Community Clothing Exchange
# Team:
Team leader: Vivek Varia
Phone: +916352630074
Email: variavivek04@gmail.com

Team member 1: Neel aghera
Phone: +91 9428232309
Email: neel.aghera23@gmail.com




The only requirement is having Node.js & npm installed - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)

Follow these steps:

```sh
# Step 1: Clone the repository using the project's Git URL.
git clone <YOUR_GIT_URL>

# Step 2: Navigate to the project directory.
cd <YOUR_PROJECT_NAME>

# Step 3: Install the necessary dependencies.
npm i

# Step 4: Start the development server with auto-reloading and an instant preview.
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
