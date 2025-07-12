#!/usr/bin/env python3
"""
Script to create a second test user account for testing the swapping mechanism.
"""

import sqlite3
import os
from datetime import datetime
from passlib.context import CryptContext

# Password handling - same as the main app
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_user():
    """Create a second test user account"""
    
    # Database path
    db_path = "rewear.db"
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if test user already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", ("testuser2@example.com",))
        existing_user = cursor.fetchone()
        
        if existing_user:
            print("Test user 2 already exists!")
            return
        
        # Create password hash using bcrypt
        password = "password123"
        password_hash = pwd_context.hash(password)
        
        # Insert new test user
        cursor.execute("""
            INSERT INTO users (email, username, password, points_balance, role, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "testuser2@example.com",
            "testuser2",
            password_hash,
            500,  # Starting points
            "user",
            datetime.now(),
            datetime.now()
        ))
        
        # Get the user ID
        user_id = cursor.lastrowid
        
        # Create some test items for the new user
        test_items = [
            {
                "title": "Vintage Denim Jacket",
                "description": "Classic vintage denim jacket in excellent condition. Perfect for layering.",
                "category": "outerwear",
                "type": "jacket",
                "size": "m",
                "condition": "good",
                "point_value": 200
            },
            {
                "title": "Leather Crossbody Bag",
                "description": "Genuine leather crossbody bag with adjustable strap. Great for everyday use.",
                "category": "accessories",
                "type": "bag",
                "size": "one_size",
                "condition": "like_new",
                "point_value": 150
            },
            {
                "title": "Floral Summer Dress",
                "description": "Beautiful floral print summer dress. Light and comfortable for warm weather.",
                "category": "dresses",
                "type": "dress",
                "size": "s",
                "condition": "good",
                "point_value": 120
            }
        ]
        
        for item in test_items:
            # Insert item
            cursor.execute("""
                INSERT INTO items (title, description, category, type, size, condition, point_value, 
                                 status, is_approved, user_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item["title"],
                item["description"],
                item["category"],
                item["type"],
                item["size"],
                item["condition"],
                item["point_value"],
                "available",
                True,  # Auto-approve for testing
                user_id,
                datetime.now(),
                datetime.now()
            ))
            
            item_id = cursor.lastrowid
            
            # Create placeholder image for each item
            image_filename = f"item_{item_id}_primary.png"
            image_url = f"/static/images/{image_filename}"
            
            cursor.execute("""
                INSERT INTO images (image_url, is_primary, item_id, created_at)
                VALUES (?, ?, ?, ?)
            """, (
                image_url,
                True,
                item_id,
                datetime.now()
            ))
        
        # Commit changes
        conn.commit()
        
        print("✅ Test user 2 created successfully!")
        print(f"📧 Email: testuser2@example.com")
        print(f"🔑 Password: password123")
        print(f"👤 Username: testuser2")
        print(f"💰 Starting points: 500")
        print(f"📦 Created {len(test_items)} test items")
        print("\nYou can now test the swapping mechanism between:")
        print("- demo@example.com (existing user)")
        print("- testuser2@example.com (new user)")
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_test_user() 