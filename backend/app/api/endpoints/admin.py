from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from app.api.deps import get_admin_user
from app.core.database import get_db
from app.models.models import Item, User
from app.schemas.schemas import Item as ItemSchema
from app.services.redis import redis_service

router = APIRouter()

@router.get("/items/pending", response_model=List[ItemSchema])
async def get_pending_items(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
) -> List[ItemSchema]:
    """
    Get items pending approval.
    """
    # Query items
    result = await db.execute(
        select(Item)
        .options(selectinload(Item.images), selectinload(Item.user))
        .where(Item.is_approved == False)
        .order_by(Item.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    items = result.scalars().all()
    
    return items

@router.put("/items/{item_id}/approve", response_model=ItemSchema)
async def approve_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
) -> ItemSchema:
    """
    Approve item.
    """
    # Query item
    result = await db.execute(
        select(Item)
        .options(selectinload(Item.images))
        .where(Item.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    
    # Update item
    item.is_approved = True
    if item.status == "pending":
        item.status = "available"
    
    await db.commit()
    await db.refresh(item)
    
    # Clear cache
    redis_service.delete(f"items:{item_id}")
    redis_service.clear_pattern("items:all:*")
    
    return item

@router.put("/items/{item_id}/reject", status_code=status.HTTP_204_NO_CONTENT)
async def reject_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
) -> None:
    """
    Reject and delete item.
    """
    # Query item
    result = await db.execute(
        select(Item)
        .options(selectinload(Item.images))
        .where(Item.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    
    # Delete item
    await db.delete(item)
    await db.commit()
    
    # Clear cache
    redis_service.delete(f"items:{item_id}")
    redis_service.clear_pattern("items:all:*")
    
    return None
