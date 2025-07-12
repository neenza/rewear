import os
import uuid
from pathlib import Path
from fastapi import UploadFile
import shutil
import aiofiles
from fastapi.staticfiles import StaticFiles

# Configuration for local storage
UPLOAD_DIR = Path("static/uploads")
BASE_URL = "/static/uploads"  # URL prefix for accessing files

class LocalStorageService:
    """Service for storing files locally instead of S3 for development/demo purposes"""
    
    def __init__(self):
        # Ensure the upload directory exists
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
    async def upload_file(self, file: UploadFile, folder: str = "images") -> str:
        """Upload file to local storage and return URL"""
        # Generate unique filename
        ext = file.filename.split('.')[-1] if '.' in file.filename else ''
        unique_filename = f"{uuid.uuid4()}.{ext}"
        
        # Create folder if it doesn't exist
        folder_path = UPLOAD_DIR / folder
        os.makedirs(folder_path, exist_ok=True)
        
        # Full path for the file
        file_path = folder_path / unique_filename
        
        # Save file
        try:
            # Reset file pointer to the beginning
            await file.seek(0)
            
            async with aiofiles.open(file_path, 'wb') as out_file:
                content = await file.read()
                await out_file.write(content)
                
            # Return URL that can be accessed via the static files mount
            return f"{BASE_URL}/{folder}/{unique_filename}"
        except Exception as e:
            print(f"Error saving file: {e}")
            raise e
    
    def delete_file(self, file_url: str) -> bool:
        """Delete file from local storage"""
        try:
            # Extract the relative path from the URL
            relative_path = file_url.replace(BASE_URL, "", 1).lstrip("/")
            file_path = UPLOAD_DIR / relative_path
            
            # Delete the file if it exists
            if file_path.exists():
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

# Create a singleton instance
local_storage_service = LocalStorageService()

# Helper function to mount the static files directory to the FastAPI app
def configure_static_files(app):
    """Configure static files serving for the uploaded files"""
    # Create the directory if it doesn't exist
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Mount the static files directory
    app.mount("/static", StaticFiles(directory="static"), name="static")
