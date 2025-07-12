from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Union
from datetime import datetime

# ------------------- User Schemas -------------------

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    profile_picture: Optional[str] = None
    password: Optional[str] = None
    
    @validator('password')
    def password_strength(cls, v):
        if v is not None and len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserInDB(UserBase):
    id: int
    profile_picture: Optional[str] = None
    points_balance: int = 0
    role: str = "user"
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class User(UserInDB):
    pass

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# ------------------- Token Schemas -------------------

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None

# ------------------- Item Schemas -------------------

class ItemBase(BaseModel):
    title: str
    description: str
    category: str
    type: str
    size: str
    condition: str
    point_value: int = Field(..., ge=0)

class ItemCreate(ItemBase):
    tags: Optional[List[str]] = []

class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    type: Optional[str] = None
    size: Optional[str] = None
    condition: Optional[str] = None
    point_value: Optional[int] = Field(None, ge=0)
    tags: Optional[List[str]] = None

class ItemInDB(ItemBase):
    id: int
    user_id: int
    status: str = "available"
    is_approved: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Item(ItemInDB):
    images: List["Image"] = []
    tags: List[str] = []
    user: Union["UserBasic", None] = None

# ------------------- Image Schemas -------------------

class ImageBase(BaseModel):
    image_url: str
    is_primary: bool = False

class ImageCreate(ImageBase):
    pass

class Image(ImageBase):
    id: int
    item_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ------------------- Swap Schemas -------------------

class SwapBase(BaseModel):
    provider_item_id: int
    requester_item_id: Optional[int] = None
    points_used: int = 0

class SwapCreate(SwapBase):
    pass

class SwapUpdate(BaseModel):
    status: str

class Swap(SwapBase):
    id: int
    requester_id: int
    provider_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    requester_item: Optional[Item] = None
    provider_item: Item
    requester: "UserBasic"
    provider: "UserBasic"

    class Config:
        from_attributes = True

# ------------------- Tag Schemas -------------------

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int
    items: List[Item] = []

    class Config:
        from_attributes = True

# ------------------- Additional helper models -------------------

class UserBasic(BaseModel):
    id: int
    username: str
    profile_picture: Optional[str] = None

    class Config:
        from_attributes = True

class ItemBasic(BaseModel):
    id: int
    title: str
    primary_image: Optional[str] = None

    class Config:
        from_attributes = True

# Update forward refs
Item.update_forward_refs()
Swap.update_forward_refs()
