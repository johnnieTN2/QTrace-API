"""
Filename: crud.py
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Item
from schema import ItemCreate, ItemUpdate
from typing import Optional

def get_item(db: Session, item_id: int) -> Optional[Item]:
    """Get a single item by ID"""
    return db.query(Item).filter(Item.id == item_id).first()

def get_items(
    db: Session, 
    skip: int = 0, 
    limit: int = 10,
    search: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    location: Optional[str] = None
):
    """Get items with optional filtering and pagination"""
    query = db.query(Item)
    
    # Apply filters
    if search:
        query = query.filter(Item.name.ilike(f"%{search}%"))
    if status:
        query = query.filter(Item.status == status)
    if category:
        query = query.filter(Item.category == category)
    if location:
        query = query.filter(Item.location.ilike(f"%{location}%"))
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination
    items = query.offset(skip).limit(limit).all()
    
    return items, total

def create_item(db: Session, item: ItemCreate) -> Item:
    """Create a new item"""
    db_item = Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_item(db: Session, item_id: int, item_update: ItemUpdate) -> Optional[Item]:
    """Update an existing item"""
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        return None
    
    # Update only fields that are provided (not None)
    update_data = item_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    # Update the updated_at timestamp
    db_item.updated_at = func.now()
    
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_item(db: Session, item_id: int) -> bool:
    """Delete an item by ID"""
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        return False
    
    db.delete(db_item)
    db.commit()
    return True

