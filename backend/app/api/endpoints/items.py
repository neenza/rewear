from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
import json

from app.api.deps import get_current_active_user, get_admin_user
from app.core.database import get_db
from app.models.models import Item, User, Image, Tag, item_tag
from app.schemas.schemas import (
    Item as ItemSchema, 
    ItemCreate, 
    ItemUpdate, 
    ImageCreate,
    TagCreate
)
# Make sure the following file exists: app/services/local_storage.py
# and contains a definition for local_storage_service.
from app.services.local_storage import local_storage_service
from app.services.redis import redis_service
import os

router = APIRouter()

@router.get("", response_model=dict)
async def get_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(12, ge=1, le=100),
    category: Optional[str] = None,
    size: Optional[str] = None, 
    condition: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve items with filtering options.
    This endpoint is public - no authentication required.
    """
    try:
        # Build the base query
        query = select(Item).options(
            selectinload(Item.images),
            selectinload(Item.tags),
            selectinload(Item.user)
        )

        # Apply filters
        if category and category != "all":
            query = query.where(Item.category == category)
        if size and size != "all":
            query = query.where(Item.size == size)
        if condition and condition != "all":
            query = query.where(Item.condition == condition)
        if search:
            search_term = f"%{search}%"
            query = query.where(Item.title.ilike(search_term) | Item.description.ilike(search_term))

        # Count total items (for pagination)
        count_query = select(func.count()).select_from(Item)
        if category and category != "all":
            count_query = count_query.where(Item.category == category)
        if size and size != "all":
            count_query = count_query.where(Item.size == size)
        if condition and condition != "all":
            count_query = count_query.where(Item.condition == condition)
        if search:
            search_term = f"%{search}%"
            count_query = count_query.where(Item.title.ilike(search_term) | Item.description.ilike(search_term))
            
        total = await db.scalar(count_query)

        # Add pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        items = result.scalars().all()
        
        return {
            "items": items,
            "total": total or 0,
            "page": skip // limit + 1,
            "pages": (total + limit - 1) // limit if total else 1
        }
        
    except Exception as e:
        print(f"Error getting items: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve items: {str(e)}")

@router.post("", response_model=ItemSchema)
async def create_item(
    item_in: str = Form(...),  # JSON string of item data
    images: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ItemSchema:
    """
    Create new item.
    """
    try:
        item_data = json.loads(item_in)
        item_create = ItemCreate(**item_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in item_in")

    db_item = Item(
        title=item_create.title,
        description=item_create.description,
        category=item_create.category,
        type=item_create.type,
        size=item_create.size,
        condition=item_create.condition,
        point_value=item_create.point_value,
        user_id=current_user.id,
        status="pending",
        is_approved=False,
    )
    db.add(db_item)

    # Process tags
    if item_create.tags:
        for tag_name in item_create.tags:
            result = await db.execute(select(Tag).where(Tag.name == tag_name))
            tag = result.scalar_one_or_none()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
            db_item.tags.append(tag)

    # Upload images
    if not images:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one image is required",
        )
    
    # Store images temporarily
    temp_images = []
    for i, image in enumerate(images):
        image_url = await local_storage_service.upload_file(image)
        temp_images.append((image_url, i == 0))

    try:
        # First commit to get the item ID
        await db.commit()
        await db.refresh(db_item)
        
        # Now add the images with the committed item ID
        for image_url, is_primary in temp_images:
            db_image = Image(
                image_url=image_url, 
                is_primary=is_primary, 
                item_id=db_item.id
            )
            db.add(db_image)
        
        # Commit again to save the images
        await db.commit()
        
        # Eagerly load relationships after commit
        await db.refresh(db_item, attribute_names=["tags", "images", "user"])
    except Exception as e:
        await db.rollback()
        # A more specific error log
        print(f"Database commit/refresh failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to save item to database.")

    # Clear cache for items
    redis_service.clear_pattern("items:*")

    return db_item
