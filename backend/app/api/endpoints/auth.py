from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.core.security import (
    verify_password, 
    create_user_token,
    get_password_hash
)
from app.models.models import User
from app.schemas.schemas import User as UserSchema
from app.schemas.schemas import UserCreate, Token, UserLogin

router = APIRouter()

@router.post("/register", response_model=UserSchema)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserSchema:
    """
    Register a new user.
    """
    # Check if user with email already exists
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Check if username is taken
    result = await db.execute(select(User).where(User.username == user_in.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    
    # Create new user
    db_user = User(
        email=user_in.email,
        username=user_in.username,
        password=get_password_hash(user_in.password),
        role="user"
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    
    # Check if user exists and password is correct
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_user_token(
        user_id=user.id,
        username=user.username,
        role=user.role
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login-email", response_model=Token)
async def login_email(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    Login with email and password, get an access token for future requests.
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()
    
    # Check if user exists and password is correct
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_user_token(
        user_id=user.id,
        username=user.username,
        role=user.role
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserSchema)
async def read_users_me(
    current_user: User = Depends(get_current_active_user),
) -> UserSchema:
    """
    Get current user.
    """
    return current_user

@router.post("/demo-login", response_model=Token)
async def demo_login(
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    Login with demo account credentials.
    """
    # Find demo user by email or create one if it doesn't exist
    demo_email = "demo@rewear.com"
    demo_password = "demopassword"
    demo_username = "demouser"
    
    # Check if demo user exists
    result = await db.execute(select(User).where(User.email == demo_email))
    user = result.scalar_one_or_none()
    
    # Create demo user if it doesn't exist
    if not user:
        db_user = User(
            email=demo_email,
            username=demo_username,
            password=get_password_hash(demo_password),
            role="user",
            points_balance=500  # Give demo user some starting points
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        user = db_user
    
    # Create access token
    access_token = create_user_token(
        user_id=user.id,
        username=user.username,
        role=user.role
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
