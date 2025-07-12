from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
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
from app.services.s3 import s3_service
from app.services.redis import redis_service

router = APIRouter()

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
    # Parse item data
    try:
        item_data = json.loads(item_in)
        item_create = ItemCreate(**item_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid item data: {str(e)}",
        )
    
    # Create item
    db_item = Item(
        title=item_create.title,
        description=item_create.description,
        category=item_create.category,
        type=item_create.type,
        size=item_create.size,
        condition=item_create.condition,
        point_value=item_create.point_value,
        user_id=current_user.id,
        # Set as pending approval
        status="pending",
        is_approved=False
    )
    db.add(db_item)
    await db.flush()
    
    # Process tags
    if item_create.tags:
        for tag_name in item_create.tags:
            # Check if tag exists
            result = await db.execute(select(Tag).where(Tag.name == tag_name))
            tag = result.scalar_one_or_none()
            
            # Create tag if it doesn't exist
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                await db.flush()
            
            # Add tag to item
            db_item.tags.append(tag)
    
    # Upload images
    for i, image in enumerate(images):
        # Upload image to S3
        image_url = await s3_service.upload_file(image)
        
        # Create image in database
        db_image = Image(
            image_url=image_url,
            is_primary=(i == 0),  # First image is primary
            item_id=db_item.id
        )
        db.add(db_image)
    
    await db.commit()
    await db.refresh(db_item)
    
    # Clear cache for items
    redis_service.clear_pattern("items:*")
    
    return db_item

@router.get("", response_model=dict)
async def get_items(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    condition: Optional[str] = None,
    size: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get all items with filtering.
    """
    # Try to get from cache
    cache_key = f"items:all:{skip}:{limit}:{category}:{condition}:{size}:{search}"
    cached_items = redis_service.get(cache_key)
    if cached_items:
        return cached_items
    
    # Build query
    query = (
        select(Item)
        .where(Item.is_approved == True, Item.status == "available")
        .options(selectinload(Item.images), selectinload(Item.tags))
        .order_by(Item.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    
    # Apply filters
    if category:
        query = query.where(Item.category == category)
    if condition:
        query = query.where(Item.condition == condition)
    if size:
        query = query.where(Item.size == size)
    if search:
        search_term = f"%{search}%"
        query = query.where(
            (Item.title.ilike(search_term)) | 
            (Item.description.ilike(search_term))
        )
    
    # Execute query
    result = await db.execute(query)
    items = result.scalars().all()
    
    # Get total count for pagination
    count_query = select(func.count(Item.id)).where(Item.is_approved == True, Item.status == "available")
    
    # Apply filters
    if category:
        count_query = count_query.where(Item.category == category)
    if condition:
        count_query = count_query.where(Item.condition == condition)
    if size:
        count_query = count_query.where(Item.size == size)
    if search:
        search_term = f"%{search}%"
        count_query = count_query.where(
            (Item.title.ilike(search_term)) | 
            (Item.description.ilike(search_term))
        )
    
    count_result = await db.execute(count_query)
    total_count = count_result.scalar_one_or_none() or 0
    
    response = {
        "items": items,
        "total": total_count
    }
    
    # Cache results
    redis_service.set(cache_key, response, expire_seconds=300)  # 5 minutes
    
    return response

@router.get("/{item_id}", response_model=ItemSchema)
async def get_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
) -> ItemSchema:
    """
    Get item by ID.
    """
    # Try to get from cache
    cache_key = f"items:{item_id}"
    cached_item = redis_service.get(cache_key)
    if cached_item:
        return cached_item
    
    # Query item with relationships
    result = await db.execute(
        select(Item)
        .options(selectinload(Item.images), selectinload(Item.tags), selectinload(Item.user))
        .where(Item.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    
    # For public access, only show approved items
    if not item.is_approved:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    
    # Cache item
    redis_service.set(cache_key, item, expire_seconds=300)  # 5 minutes
    
    return item

@router.put("/{item_id}", response_model=ItemSchema)
async def update_item(
    item_id: int,
    item_update: ItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ItemSchema:
    """
    Update item.
    """
    # Query item
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    
    # Check if user is the owner
    if item.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Update fields if provided
    if item_update.title is not None:
        item.title = item_update.title
    if item_update.description is not None:
        item.description = item_update.description
    if item_update.category is not None:
        item.category = item_update.category
    if item_update.type is not None:
        item.type = item_update.type
    if item_update.size is not None:
        item.size = item_update.size
    if item_update.condition is not None:
        item.condition = item_update.condition
    if item_update.point_value is not None:
        item.point_value = item_update.point_value
    
    # Update tags if provided
    if item_update.tags is not None:
        # Clear existing tags
        item.tags = []
        
        # Add new tags
        for tag_name in item_update.tags:
            # Check if tag exists
            result = await db.execute(select(Tag).where(Tag.name == tag_name))
            tag = result.scalar_one_or_none()
            
            # Create tag if it doesn't exist
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                await db.flush()
            
            # Add tag to item
            item.tags.append(tag)
    
    # If user updates item, mark as not approved
    if current_user.role != "admin":
        item.is_approved = False
        item.status = "pending"
    
    await db.commit()
    await db.refresh(item)
    
    # Clear cache
    redis_service.delete(f"items:{item_id}")
    redis_service.clear_pattern("items:all:*")
    
    return item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Delete item.
    """
    # Query item
    result = await db.execute(select(Item).options(selectinload(Item.images)).where(Item.id == item_id))
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    
    # Check if user is the owner or admin
    if item.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Delete images from S3
    for image in item.images:
        s3_service.delete_file(image.image_url)
    
    # Delete item from database
    await db.delete(item)
    await db.commit()
    
    # Clear cache
    redis_service.delete(f"items:{item_id}")
    redis_service.clear_pattern("items:all:*")
    
    return None
