#!/usr/bin/env python3
"""
Script to migrate existing image URLs from placeholder URLs to local static paths.
This updates the database to use local image URLs instead of external placeholder URLs.
"""

import sqlite3
import os
import shutil
from pathlib import Path

def migrate_images():
    """Migrate existing image URLs to local static paths"""
    
    # Database path
    db_path = "rewear.db"
    
    # Static images directory
    static_dir = Path("app/static/images")
    static_dir.mkdir(parents=True, exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get all images with placeholder URLs
        cursor.execute("""
            SELECT id, image_url, item_id, is_primary 
            FROM images 
            WHERE image_url LIKE '%via.placeholder.com%' OR image_url LIKE '%placeholder.com%'
        """)
        
        images = cursor.fetchall()
        print(f"Found {len(images)} images to migrate")
        
        for img_id, old_url, item_id, is_primary in images:
            # Create a simple local image path
            # For now, we'll create a simple placeholder image
            new_filename = f"item_{item_id}_{'primary' if is_primary else 'secondary'}.png"
            new_url = f"/static/images/{new_filename}"
            
            # Create a simple colored placeholder image using PIL or just copy a basic one
            # For simplicity, we'll just create an empty file for now
            placeholder_path = static_dir / new_filename
            if not placeholder_path.exists():
                # Create a simple text file as placeholder (you can replace this with actual image generation)
                with open(placeholder_path, 'w') as f:
                    f.write(f"Placeholder for item {item_id}")
            
            # Update the database
            cursor.execute("""
                UPDATE images 
                SET image_url = ? 
                WHERE id = ?
            """, (new_url, img_id))
            
            print(f"Migrated image {img_id}: {old_url} -> {new_url}")
        
        # Commit changes
        conn.commit()
        print(f"Successfully migrated {len(images)} images")
        
        # Show updated data
        cursor.execute("SELECT id, image_url FROM images LIMIT 5")
        updated_images = cursor.fetchall()
        print("\nUpdated image URLs:")
        for img_id, url in updated_images:
            print(f"  {img_id}: {url}")
            
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_images() 