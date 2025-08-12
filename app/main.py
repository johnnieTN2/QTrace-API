'''
Filename:  main.py

@app.get("/")  # Root endpoint - welcome message
@app.get("/health")  # Health check endpoint  
@app.get("/items/")  # Get ALL items (with filtering/pagination)
@app.get("/items/{item_id}")  # Get ONE specific item by ID


'''
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from database import test_connection, create_tables, get_db
from models import Item
from schema import ItemCreate, ItemUpdate, ItemResponse, ItemList
from crud import get_item, get_items, create_item, update_item, delete_item
import uvicorn
import math


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for startup and shutdown tasks.
    This replaces the deprecated @app.on_event("startup") decorator.
    """
    # Startup tasks
    print("🚀 Starting Item Tracker API...")
    
    # Test database connection
    if test_connection():
        print("📊 Database connection verified")
        
        # Create tables (will only create if they don't exist)
        if create_tables():
            print("📋 Database tables ready")
        else:
            print("⚠️  Warning: Table creation had issues")
    else:
        print("⚠️  Warning: Database connection failed during startup")
    
    yield  # This is where the app runs
    
    # Shutdown tasks (if needed in future)
    print("🛑 Shutting down Item Tracker API...")


# Create FastAPI app instance with lifespan handler
app = FastAPI(
    title="Item Tracker API",
    description="A personal item tracking system",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    """Root endpoint - API welcome message"""
    return {
        "message": "Welcome to Item Tracker API!",
        "version": "1.0.0",
        "docs": "/docs",
        "models": "Item model loaded"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint that includes database connectivity status.
    Useful for monitoring and deployment health checks.
    """
    db_status = test_connection()
    return {
        "status": "healthy" if db_status else "degraded",
        "database": "connected" if db_status else "disconnected",
        "api": "running",
        "models": "Item model available"
    }

@app.post("/items/", response_model=ItemResponse)
async def create_new_item(item: ItemCreate, db: Session = Depends(get_db)):
    """Create a new item"""
    try:
        db_item = create_item(db=db, item=item)
        return db_item
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating item: {str(e)}")
    
@app.get("/items/", response_model=ItemList)
async def read_items(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return"),
    search: str = Query(None, description="Search items by name"),
    status: str = Query(None, description="Filter by status"),
    category: str = Query(None, description="Filter by category"),
    location: str = Query(None, description="Filter by location"),
    db: Session = Depends(get_db)
):
    """Get all items with optional filtering and pagination"""
    items, total = get_items(
        db=db, skip=skip, limit=limit, 
        search=search, status=status, category=category, location=location
    )
    
    pages = math.ceil(total / limit) if total > 0 else 1
    page = (skip // limit) + 1
    
    return ItemList(
        items=items,
        total=total,
        page=page,
        per_page=limit,
        pages=pages
    )

@app.get("/items/{item_id}", response_model=ItemResponse)
async def read_item(item_id: int, db: Session = Depends(get_db)):
    """Get a single item by ID"""
    db_item = get_item(db=db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.put("/items/{item_id}", response_model=ItemResponse)
async def update_existing_item(item_id: int, item_update: ItemUpdate, db: Session = Depends(get_db)):
    """Update an existing item"""
    db_item = update_item(db=db, item_id=item_id, item_update=item_update)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.delete("/items/{item_id}")
async def delete_existing_item(item_id: int, db: Session = Depends(get_db)):
    """Delete an item"""
    success = delete_item(db=db, item_id=item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}



# Change the uvicorn run line at bottom
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)