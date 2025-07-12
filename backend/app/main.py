import sys
from pathlib import Path

# Add project root to the Python path
# This is the directory that contains the 'app' folder
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.api import api_router
from app.core.config import settings
from app.services.local_storage import configure_static_files

app = FastAPI(
    title="ReWear API",
    description="API for the ReWear clothing exchange platform",
    version="1.0.0"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure static files for local storage
configure_static_files(app)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to the ReWear API! Check out /docs for the API documentation."}
