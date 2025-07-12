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
        # Auto-approve for development
        status="available",
        is_approved=True
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
            
            # Add tag to item using direct insertion into junction table
            await db.execute(
                item_tag.insert().values(item_id=db_item.id, tag_id=tag.id)
            )
    
    # Upload images
    import os
    import uuid
    from fastapi import Request
    STATIC_IMAGE_PATH = os.path.join(os.path.dirname(__file__), '../../static/images')
    os.makedirs(STATIC_IMAGE_PATH, exist_ok=True)
    for i, image in enumerate(images):
        try:
            # Save image to local static directory
            ext = os.path.splitext(image.filename)[1]
            unique_filename = f"{uuid.uuid4().hex}{ext}"
            file_path = os.path.join(STATIC_IMAGE_PATH, unique_filename)
            with open(file_path, "wb") as buffer:
                buffer.write(await image.read())
            image_url = f"/static/images/{unique_filename}"
        except Exception as e:
            print(f"Local image save failed: {e}")
            image_url = f"/static/images/placeholder.png"
        
        # Create image in database
        db_image = Image(
            image_url=image_url,
            is_primary=(i == 0),  # First image is primary
            item_id=db_item.id
        )
        db.add(db_image)
    
    await db.commit()
    # Refresh the item and its images from the database
    await db.refresh(db_item)
    result = await db.execute(
        select(Item)
        .options(selectinload(Item.images), selectinload(Item.tags))
        .where(Item.id == db_item.id)
    )
    db_item = result.scalar_one_or_none()
    
    # Convert tags to strings to match schema expectation
    if db_item and hasattr(db_item, 'tags'):
        # Convert images to dictionaries
        images_list = []
        if db_item.images:
            for image in db_item.images:
                images_list.append({
                    'id': image.id,
                    'image_url': image.image_url,
                    'is_primary': image.is_primary,
                    'item_id': image.item_id,
                    'created_at': image.created_at
                })
        
        # Create a copy of the item with tags as strings
        item_dict = {
            'id': db_item.id,
            'title': db_item.title,
            'description': db_item.description,
            'category': db_item.category,
            'type': db_item.type,
            'size': db_item.size,
            'condition': db_item.condition,
            'point_value': db_item.point_value,
            'user_id': db_item.user_id,
            'status': db_item.status,
            'is_approved': db_item.is_approved,
            'created_at': db_item.created_at,
            'updated_at': db_item.updated_at,
            'images': images_list,
            'tags': [tag.name for tag in db_item.tags] if db_item.tags else [],
            'user': None  # We'll load this separately if needed
        }
        db_item = item_dict
    
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
    
    # Convert items to proper format to avoid serialization issues
    formatted_items = []
    for item in items:
        # Convert images to dictionaries
        images_list = []
        if item.images:
            for image in item.images:
                images_list.append({
                    'id': image.id,
                    'image_url': image.image_url,
                    'is_primary': image.is_primary,
                    'item_id': image.item_id,
                    'created_at': image.created_at
                })
        
        item_dict = {
            'id': item.id,
            'title': item.title,
            'description': item.description,
            'category': item.category,
            'type': item.type,
            'size': item.size,
            'condition': item.condition,
            'point_value': item.point_value,
            'user_id': item.user_id,
            'status': item.status,
            'is_approved': item.is_approved,
            'created_at': item.created_at,
            'updated_at': item.updated_at,
            'images': images_list,
            'tags': [tag.name for tag in item.tags] if item.tags else [],
            'user': None
        }
        formatted_items.append(item_dict)
    
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
        "items": formatted_items,
        "total": total_count
    }
    
    # Cache results
    redis_service.set(cache_key, response, expire_seconds=300)  # 5 minutes
    
    return response

@router.get("/my-items", response_model=dict)
async def get_my_items(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """
    Get current user's items (including pending and unapproved).
    """
    # Build query for user's items
    query = (
        select(Item)
        .where(Item.user_id == current_user.id)
        .options(selectinload(Item.images), selectinload(Item.tags))
        .order_by(Item.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    
    # Execute query
    result = await db.execute(query)
    items = result.scalars().all()
    
    # Get total count
    count_query = select(func.count(Item.id)).where(Item.user_id == current_user.id)
    count_result = await db.execute(count_query)
    total_count = count_result.scalar_one_or_none() or 0
    
    # Convert items to proper format
    formatted_items = []
    for item in items:
        # Convert images to dictionaries
        images_list = []
        if item.images:
            for image in item.images:
                images_list.append({
                    'id': image.id,
                    'image_url': image.image_url,
                    'is_primary': image.is_primary,
                    'item_id': image.item_id,
                    'created_at': image.created_at
                })
        
        item_dict = {
            'id': item.id,
            'title': item.title,
            'description': item.description,
            'category': item.category,
            'type': item.type,
            'size': item.size,
            'condition': item.condition,
            'point_value': item.point_value,
            'user_id': item.user_id,
            'status': item.status,
            'is_approved': item.is_approved,
            'created_at': item.created_at,
            'updated_at': item.updated_at,
            'images': images_list,
            'tags': [tag.name for tag in item.tags] if item.tags else [],
            'user': None
        }
        formatted_items.append(item_dict)
    
    response = {
        "items": formatted_items,
        "total": total_count
    }
    
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
    
    # Convert item to proper format to avoid serialization issues
    # Convert images to dictionaries
    images_list = []
    if item.images:
        for image in item.images:
            images_list.append({
                'id': image.id,
                'image_url': image.image_url,
                'is_primary': image.is_primary,
                'item_id': image.item_id,
                'created_at': image.created_at
            })
    
    # Convert user to dictionary
    user_dict = None
    if item.user:
        user_dict = {
            'id': item.user.id,
            'email': item.user.email,
            'username': item.user.username,
            'profile_picture': item.user.profile_picture,
            'points_balance': item.user.points_balance,
            'role': item.user.role,
            'created_at': item.user.created_at,
            'updated_at': item.user.updated_at
        }
    
    item_dict = {
        'id': item.id,
        'title': item.title,
        'description': item.description,
        'category': item.category,
        'type': item.type,
        'size': item.size,
        'condition': item.condition,
        'point_value': item.point_value,
        'user_id': item.user_id,
        'status': item.status,
        'is_approved': item.is_approved,
        'created_at': item.created_at,
        'updated_at': item.updated_at,
        'images': images_list,
        'tags': [tag.name for tag in item.tags] if item.tags else [],
        'user': user_dict
    }
    
    # Cache the converted item
    redis_service.set(cache_key, item_dict, expire_seconds=300)  # 5 minutes
    
    return item_dict

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
    # REMOVE S3 delete_file in delete_item endpoint
    
    # Delete item from database
    await db.delete(item)
    await db.commit()
    
    # Clear cache
    redis_service.delete(f"items:{item_id}")
    redis_service.clear_pattern("items:all:*")
    
    return None
