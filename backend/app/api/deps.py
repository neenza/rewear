from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from pydantic import ValidationError
from typing import Optional, Dict, Any

from app.core.database import get_db
from app.core.security import SECRET_KEY, ALGORITHM, TokenData
from app.models.models import User
from sqlalchemy import select

# OAuth2 password bearer scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Get current user from token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data_dict = payload.get("sub")
        if token_data_dict is None:
            raise credentials_exception
            
        # Parse the token data
        try:
            # Handle both string and dict formats
            if isinstance(token_data_dict, str):
                import json
                token_data_dict = json.loads(token_data_dict)
            
            token_data = TokenData(**token_data_dict)
        except (ValidationError, ValueError):
            raise credentials_exception
        
        if token_data.user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
        
    # Get user from database
    result = await db.execute(select(User).where(User.id == token_data.user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
        
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Check if current user is active.
    """
    # You can add additional checks here, e.g., is_active field
    return current_user

async def get_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Check if current user is an admin.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user
