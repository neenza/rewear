import asyncio
import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import AsyncSessionLocal
from app.models.models import User, Item, Image, Tag

# Demo item data
items_data = [
    {
        "title": "White Summer Dress",
        "description": "Elegant white summer dress, perfect for beach days and casual outings. Light fabric, comfortable fit.",
        "category": "dresses",
        "type": "casual",
        "size": "m",
        "condition": "like_new",
        "point_value": 120,
        "status": "available",
        "is_approved": True,
        "image_url": "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?q=80&w=500",
        "tags": ["summer", "white", "casual", "dress"]
    },
    {
        "title": "Blue Denim Jacket",
        "description": "Classic denim jacket in blue. Goes well with any outfit, slightly worn but in excellent condition.",
        "category": "outerwear",
        "type": "casual",
        "size": "l",
        "condition": "good",
        "point_value": 150,
        "status": "available",
        "is_approved": True,
        "image_url": "https://images.unsplash.com/photo-1542272604-787c3835535d?q=80&w=500",
        "tags": ["denim", "jacket", "casual", "blue"]
    },
    {
        "title": "Red Party Heels",
        "description": "Stunning red heels, perfect for parties and special occasions. Worn once, like new condition.",
        "category": "shoes",
        "type": "formal",
        "size": "s",
        "condition": "like_new",
        "point_value": 200,
        "status": "available",
        "is_approved": True,
        "image_url": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?q=80&w=500",
        "tags": ["shoes", "heels", "red", "party"]
    },
    {
        "title": "Black Leather Jacket",
        "description": "Stylish black leather jacket, great for fall and winter. Minor wear but overall excellent condition.",
        "category": "outerwear",
        "type": "casual",
        "size": "m",
        "condition": "good",
        "point_value": 300,
        "status": "available",
        "is_approved": True,
        "image_url": "https://images.unsplash.com/photo-1551028719-00167b16eac5?q=80&w=500",
        "tags": ["leather", "jacket", "black", "winter"]
    },
    {
        "title": "Striped T-Shirt",
        "description": "Classic navy and white striped t-shirt, cotton material. Very comfortable for everyday wear.",
        "category": "tops",
        "type": "casual",
        "size": "s",
        "condition": "good",
        "point_value": 80,
        "status": "available",
        "is_approved": True,
        "image_url": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?q=80&w=500",
        "tags": ["tshirt", "striped", "casual", "cotton"]
    },
    {
        "title": "Green Sweater",
        "description": "Warm green sweater, perfect for fall and winter. Soft wool blend material.",
        "category": "tops",
        "type": "casual",
        "size": "xl",
        "condition": "good",
        "point_value": 100,
        "status": "available",
        "is_approved": True,
        "image_url": "https://images.unsplash.com/photo-1580331451432-79c5ec35b606?q=80&w=500",
        "tags": ["sweater", "green", "winter", "wool"]
    },
    {
        "title": "Black Jeans",
        "description": "Classic black jeans, straight cut. Versatile and goes with everything.",
        "category": "bottoms",
        "type": "casual",
        "size": "m",
        "condition": "good",
        "point_value": 90,
        "status": "available",
        "is_approved": True,
        "image_url": "https://images.unsplash.com/photo-1584370848010-d7fe6bc767ec?q=80&w=500",
        "tags": ["jeans", "black", "casual", "denim"]
    },
    {
        "title": "Floral Summer Skirt",
        "description": "Beautiful floral print skirt, perfect for summer days. Light and flowy material.",
        "category": "bottoms",
        "type": "casual",
        "size": "s",
        "condition": "like_new",
        "point_value": 110,
        "status": "available",
        "is_approved": True,
        "image_url": "https://images.unsplash.com/photo-1577900232427-18219b9166a0?q=80&w=500",
        "tags": ["skirt", "floral", "summer", "casual"]
    },
    {
        "title": "Navy Blue Blazer",
        "description": "Professional navy blue blazer, perfect for office wear or formal occasions.",
        "category": "outerwear",
        "type": "formal",
        "size": "l",
        "condition": "good",
        "point_value": 250,
        "status": "available",
        "is_approved": True,
        "image_url": "https://images.unsplash.com/photo-1598808503746-f34c53b9323e?q=80&w=500",
        "tags": ["blazer", "navy", "formal", "office"]
    },
    {
        "title": "Brown Leather Handbag",
        "description": "Elegant brown leather handbag with multiple compartments. Great condition with minimal wear.",
        "category": "accessories",
        "type": "casual",
        "size": "m",
        "condition": "good",
        "point_value": 180,
        "status": "available",
        "is_approved": True,
        "image_url": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?q=80&w=500",
        "tags": ["handbag", "leather", "brown", "accessories"]
    },
    {
        "title": "White Sneakers",
        "description": "Clean white sneakers, comfortable for everyday wear. Slight scuffs but overall good condition.",
        "category": "shoes",
        "type": "casual",
        "size": "l",
        "condition": "good",
        "point_value": 130,
        "status": "available",
        "is_approved": True,
        "image_url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?q=80&w=500",
        "tags": ["sneakers", "white", "casual", "shoes"]
    },
    {
        "title": "Polka Dot Blouse",
        "description": "Cute polka dot blouse, perfect for work or casual outings. Light and airy material.",
        "category": "tops",
        "type": "casual",
        "size": "s",
        "condition": "like_new",
        "point_value": 95,
        "status": "available",
        "is_approved": True,
        "image_url": "https://images.unsplash.com/photo-1602421115368-ec48466a5534?q=80&w=500",
        "tags": ["blouse", "polka dot", "casual", "tops"]
    }
]

async def add_demo_items():
    async with AsyncSessionLocal() as session:
        # Get the demo user
        result = await session.execute(select(User).where(User.email == "demo@rewear.com"))
        demo_user = result.scalar_one_or_none()
        
        if not demo_user:
            print("Demo user not found. Please run init_db.py first.")
            return
        
        # Check if we already have items
        result = await session.execute(select(Item))
        existing_items = result.scalars().all()
        
        if existing_items:
            print(f"Database already has {len(existing_items)} items. Skipping item creation.")
            return
        
        print("Adding demo items...")
        
        # Create dates for items (spread over the last month)
        now = datetime.now()
        
        for i, item_data in enumerate(items_data):
            # Create random date within the last month
            days_ago = random.randint(1, 30)
            created_date = now - timedelta(days=days_ago)
            
            # Create the item
            item = Item(
                title=item_data["title"],
                description=item_data["description"],
                category=item_data["category"],
                type=item_data["type"],
                size=item_data["size"],
                condition=item_data["condition"],
                point_value=item_data["point_value"],
                status=item_data["status"],
                is_approved=item_data["is_approved"],
                user_id=demo_user.id,
                created_at=created_date,
                updated_at=created_date
            )
            
            session.add(item)
            # Flush to get the item ID
            await session.flush()
            
            # Add image
            image = Image(
                image_url=item_data["image_url"],
                is_primary=True,
                item_id=item.id
            )
            session.add(image)
            
            # Add tags
            for tag_name in item_data["tags"]:
                # Check if tag exists
                result = await session.execute(select(Tag).where(Tag.name == tag_name))
                tag = result.scalar_one_or_none()
                
                if not tag:
                    tag = Tag(name=tag_name)
                    session.add(tag)
                    await session.flush()
                
                # Add tag to item
                item.tags.append(tag)
            
            print(f"Created item: {item.title}")
        
        # Commit all changes
        await session.commit()
        print(f"Added {len(items_data)} demo items to the database")

if __name__ == "__main__":
    asyncio.run(add_demo_items())
