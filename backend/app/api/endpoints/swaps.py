from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.models import Swap, Item, User
from app.schemas.schemas import Swap as SwapSchema, SwapCreate, SwapUpdate
from app.services.redis import redis_service

router = APIRouter()

@router.post("", response_model=SwapSchema)
async def create_swap(
    swap_in: SwapCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SwapSchema:
    """
    Request a swap.
    """
    # Get provider item
    result = await db.execute(select(Item).where(Item.id == swap_in.provider_item_id))
    provider_item = result.scalar_one_or_none()
    
    if not provider_item or not provider_item.is_approved or provider_item.status != "available":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found or not available",
        )
    
    # Check if user is not the owner
    if provider_item.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot request swap for your own item",
        )
    
    # Check if item swap or points swap
    if swap_in.requester_item_id:
        # Item swap
        # Get requester item
        result = await db.execute(select(Item).where(Item.id == swap_in.requester_item_id))
        requester_item = result.scalar_one_or_none()
        
        if not requester_item or not requester_item.is_approved or requester_item.status != "available":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Your item not found or not available",
            )
        
        # Check if user is the owner
        if requester_item.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You can only offer your own items",
            )
        
        # Create swap
        db_swap = Swap(
            requester_id=current_user.id,
            provider_id=provider_item.user_id,
            requester_item_id=swap_in.requester_item_id,
            provider_item_id=swap_in.provider_item_id,
            points_used=0,
            status="requested"
        )
        
        # Mark items as pending
        requester_item.status = "pending"
        
    else:
        # Points swap
        points_needed = provider_item.point_value
        
        # Check if user has enough points
        if current_user.points_balance < points_needed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough points. You need {points_needed} points, but have {current_user.points_balance}.",
            )
        
        # Create swap
        db_swap = Swap(
            requester_id=current_user.id,
            provider_id=provider_item.user_id,
            requester_item_id=None,
            provider_item_id=swap_in.provider_item_id,
            points_used=points_needed,
            status="requested"
        )
    
    # Mark provider item as pending
    provider_item.status = "pending"
    
    db.add(db_swap)
    await db.commit()
    await db.refresh(db_swap)
    
    # Clear cache
    redis_service.clear_pattern("items:*")
    redis_service.clear_pattern("swaps:*")
    
    return db_swap

@router.get("", response_model=List[SwapSchema])
async def get_swaps(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[SwapSchema]:
    """
    Get user's swaps.
    """
    # Try to get from cache
    cache_key = f"swaps:user:{current_user.id}"
    cached_swaps = redis_service.get(cache_key)
    if cached_swaps:
        return cached_swaps
    
    # Query swaps
    result = await db.execute(
        select(Swap)
        .options(
            selectinload(Swap.requester),
            selectinload(Swap.provider),
            selectinload(Swap.requester_item),
            selectinload(Swap.provider_item)
        )
        .where(
            (Swap.requester_id == current_user.id) | 
            (Swap.provider_id == current_user.id)
        )
        .order_by(Swap.created_at.desc())
    )
    swaps = result.scalars().all()
    
    # Cache results
    redis_service.set(cache_key, [swap for swap in swaps], expire_seconds=300)  # 5 minutes
    
    return swaps

@router.get("/{swap_id}", response_model=SwapSchema)
async def get_swap(
    swap_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SwapSchema:
    """
    Get swap by ID.
    """
    # Try to get from cache
    cache_key = f"swaps:{swap_id}"
    cached_swap = redis_service.get(cache_key)
    if cached_swap:
        return cached_swap
    
    # Query swap
    result = await db.execute(
        select(Swap)
        .options(
            selectinload(Swap.requester),
            selectinload(Swap.provider),
            selectinload(Swap.requester_item),
            selectinload(Swap.provider_item)
        )
        .where(Swap.id == swap_id)
    )
    swap = result.scalar_one_or_none()
    
    if not swap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Swap not found",
        )
    
    # Check if user is part of the swap
    if swap.requester_id != current_user.id and swap.provider_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Cache swap
    redis_service.set(cache_key, swap, expire_seconds=300)  # 5 minutes
    
    return swap

@router.put("/{swap_id}", response_model=SwapSchema)
async def update_swap(
    swap_id: int,
    swap_update: SwapUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SwapSchema:
    """
    Update swap status (accept/reject/complete).
    """
    # Query swap
    result = await db.execute(
        select(Swap)
        .options(
            selectinload(Swap.requester_item),
            selectinload(Swap.provider_item)
        )
        .where(Swap.id == swap_id)
    )
    swap = result.scalar_one_or_none()
    
    if not swap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Swap not found",
        )
    
    # Check permissions
    if swap_update.status == "rejected":
        # Both requester and provider can reject
        if swap.requester_id != current_user.id and swap.provider_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
    elif swap_update.status == "accepted":
        # Only provider can accept
        if swap.provider_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
    elif swap_update.status == "completed":
        # Both parties must agree, but only provider can mark as completed
        if swap.provider_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        # Check if swap is accepted
        if swap.status != "accepted":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only complete accepted swaps",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status",
        )
    
    # Get associated users
    result = await db.execute(
        select(User).where(
            (User.id == swap.requester_id) | 
            (User.id == swap.provider_id)
        )
    )
    users = result.scalars().all()
    requester = next((user for user in users if user.id == swap.requester_id), None)
    provider = next((user for user in users if user.id == swap.provider_id), None)
    
    # Handle status change
    if swap_update.status == "rejected":
        # Free up items
        if swap.provider_item:
            swap.provider_item.status = "available"
        
        if swap.requester_item:
            swap.requester_item.status = "available"
        
    elif swap_update.status == "accepted":
        # Items remain in pending state
        pass
        
    elif swap_update.status == "completed":
        # Process the swap
        
        # For points swap
        if not swap.requester_item_id and swap.points_used > 0:
            # Deduct points from requester
            requester.points_balance -= swap.points_used
            # Add points to provider
            provider.points_balance += swap.points_used
            # Mark provider item as swapped
            swap.provider_item.status = "swapped"
        else:
            # For item swap
            # Mark both items as swapped
            if swap.provider_item:
                swap.provider_item.status = "swapped"
            if swap.requester_item:
                swap.requester_item.status = "swapped"
    
    # Update swap status
    swap.status = swap_update.status
    
    await db.commit()
    await db.refresh(swap)
    
    # Clear cache
    redis_service.delete(f"swaps:{swap_id}")
    redis_service.clear_pattern("swaps:user:*")
    redis_service.clear_pattern("items:*")
    
    return swap
