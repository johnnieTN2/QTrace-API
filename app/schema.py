from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ItemBase(BaseModel):
    """Base schema with common Item fields"""
    name: str = Field(..., min_length=1, max_length=255, description="Item name")
    description: Optional[str] = Field(None, description="Item description")
    location: Optional[str] = Field(None, max_length=255, description="Item location")
    status: str = Field(default="active", max_length=50, description="Item status")
    category: Optional[str] = Field(None, max_length=100, description="Item category")
    is_fragile: bool = Field(default=False, description="Whether item is fragile")
    image_url: Optional[str] = Field(None, max_length=500, description="Image URL")

class ItemCreate(ItemBase):
    """Schema for creating new items (POST requests)"""
    # Inherits all fields from ItemBase
    # All validation rules come from parent class
    pass

class ItemUpdate(BaseModel):
    """Schema for updating items (PUT/PATCH requests)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=255)
    status: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=100)
    is_fragile: Optional[bool] = None
    image_url: Optional[str] = Field(None, max_length=500)

class ItemResponse(ItemBase):
    """Schema for item responses (GET requests)"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Enables ORM mode for SQLAlchemy models

class ItemList(BaseModel):
    """Schema for paginated item lists"""
    items: list[ItemResponse]
    total: int
    page: int = 1
    per_page: int = 10
    pages: int

class StatusOptions(BaseModel):
    """Available status options for items"""
    statuses: list[str] = ["active", "stored", "lost", "donated", "sold"]