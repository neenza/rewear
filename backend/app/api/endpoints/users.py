from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.api.deps import get_current_active_user, get_admin_user
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.models import User, Item
from app.schemas.schemas import User as UserSchema
from app.schemas.schemas import UserUpdate, Item as ItemSchema

router = APIRouter()

@router.get("/profile", response_model=UserSchema)
async def get_user_profile(
    current_user: User = Depends(get_current_active_user),
) -> UserSchema:
    """
    Get current user profile.
    """
    return current_user

@router.put("/profile", response_model=UserSchema)
async def update_user_profile(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> UserSchema:
    """
    Update current user profile.
    """
    # Update user fields if provided
    if user_update.email is not None:
        # Check if email is already taken
        result = await db.execute(
            select(User).where(
                User.email == user_update.email,
                User.id != current_user.id
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        current_user.email = user_update.email
    
    if user_update.username is not None:
        # Check if username is already taken
        result = await db.execute(
            select(User).where(
                User.username == user_update.username,
                User.id != current_user.id
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )
        current_user.username = user_update.username
    
    if user_update.profile_picture is not None:
        current_user.profile_picture = user_update.profile_picture
    
    if user_update.password is not None:
        current_user.password = get_password_hash(user_update.password)
    
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    
    return current_user

@router.get("/{user_id}/items", response_model=List[ItemSchema])
async def get_user_items(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[ItemSchema]:
    """
    Get user's items.
    """
    # Query user items
    result = await db.execute(
        select(Item)
        .where(Item.user_id == user_id, Item.is_approved == True)
        .order_by(Item.created_at.desc())
    )
    items = result.scalars().all()
    
    # Check if viewing own items or items are public
    if user_id != current_user.id:
        # Filter out non-public items
        items = [item for item in items if item.status == "available"]
    
    return items
