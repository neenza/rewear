from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Float, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

# Junction table for items and tags
item_tag = Table(
    "item_tag",
    Base.metadata,
    Column("item_id", Integer, ForeignKey("items.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    profile_picture = Column(String, nullable=True)
    points_balance = Column(Integer, default=0)
    role = Column(String, default="user")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    items = relationship("Item", back_populates="user")
    requested_swaps = relationship("Swap", foreign_keys="Swap.requester_id", back_populates="requester")
    provided_swaps = relationship("Swap", foreign_keys="Swap.provider_id", back_populates="provider")

class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False)
    category = Column(String, nullable=False)
    type = Column(String, nullable=False)
    size = Column(String, nullable=False)
    condition = Column(String, nullable=False)
    point_value = Column(Integer, nullable=False)
    status = Column(String, default="available")
    is_approved = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="items")
    images = relationship("Image", back_populates="item", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=item_tag, back_populates="items")
    requester_swaps = relationship("Swap", foreign_keys="Swap.requester_item_id", back_populates="requester_item")
    provider_swaps = relationship("Swap", foreign_keys="Swap.provider_item_id", back_populates="provider_item")

class Image(Base):
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String, nullable=False)
    is_primary = Column(Boolean, default=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    item = relationship("Item", back_populates="images")

class Swap(Base):
    __tablename__ = "swaps"
    
    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    requester_item_id = Column(Integer, ForeignKey("items.id"), nullable=True)
    provider_item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    points_used = Column(Integer, default=0)
    status = Column(String, default="requested")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    requester = relationship("User", foreign_keys=[requester_id], back_populates="requested_swaps")
    provider = relationship("User", foreign_keys=[provider_id], back_populates="provided_swaps")
    requester_item = relationship("Item", foreign_keys=[requester_item_id], back_populates="requester_swaps")
    provider_item = relationship("Item", foreign_keys=[provider_item_id], back_populates="provider_swaps")

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    
    # Relationships
    items = relationship("Item", secondary=item_tag, back_populates="tags")
