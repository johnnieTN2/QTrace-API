from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func
from database import Base

class Item(Base):
    """
    SQLAlchemy model for the items table.
    Represents personal items being tracked in the system.
    """
    __tablename__ = "items"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Required fields
    name = Column(String(255), nullable=False, index=True)
    
    # Optional fields
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True, index=True)
    status = Column(String(50), nullable=False, default='active', index=True)
    category = Column(String(100), nullable=True, index=True)
    is_fragile = Column(Boolean, nullable=False, default=False)
    
    # Timestamp fields (auto-managed)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Image storage
    image_url = Column(String(500), nullable=True)
    
    def __repr__(self):
        """String representation of the Item object for debugging"""
        return f"<Item(id={self.id}, name='{self.name}', status='{self.status}')>"
    
    def to_dict(self):
        """Convert Item object to dictionary for easy JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'location': self.location,
            'status': self.status,
            'category': self.category,
            'is_fragile': self.is_fragile,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'image_url': self.image_url
        }