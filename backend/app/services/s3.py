import boto3
import os
from dotenv import load_dotenv
import uuid
from fastapi import UploadFile

# Load environment variables
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

class S3Service:
    """Service for uploading files to S3"""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        self.bucket_name = AWS_STORAGE_BUCKET_NAME
        
    async def upload_file(self, file: UploadFile, folder: str = "images") -> str:
        """Upload file to S3 and return URL"""
        # Generate unique filename
        ext = file.filename.split('.')[-1] if '.' in file.filename else ''
        unique_filename = f"{folder}/{uuid.uuid4()}.{ext}"
        
        # Upload file
        contents = await file.read()
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=unique_filename,
            Body=contents,
            ContentType=file.content_type
        )
        
        # Return URL
        return f"https://{self.bucket_name}.s3.{AWS_REGION}.amazonaws.com/{unique_filename}"
    
    def delete_file(self, file_url: str) -> bool:
        """Delete file from S3"""
        try:
            # Extract the key from the URL
            key = file_url.split(f"{self.bucket_name}.s3.{AWS_REGION}.amazonaws.com/")[1]
            
            # Delete the object
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

# Singleton instance
s3_service = S3Service()
