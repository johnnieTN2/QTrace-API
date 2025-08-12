'''
Filename:  main.py

@app.get("/")  # Root endpoint - welcome message
@app.get("/health")  # Health check endpoint  
@app.get("/items/")  # Get ALL items (with filtering/pagination)
@app.get("/items/{item_id}")  # Get ONE specific item by ID


'''
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import uvicorn

# Fix these imports to use relative imports
from .database import test_connection, create_tables, get_db
from .models import Item
from .schemas import ItemCreate, ItemUpdate, ItemResponse
from . import crud



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
app = FastAPI(title="QTrace API", description="Item tracking system", version="1.0.0")


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    test_connection()
    create_tables()

@app.get("/")
def read_root():
    return {"message": "QTrace API is running!"}

@app.post("/items/", response_model=ItemResponse)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    return crud.create_item(db=db, item=item)

@app.get("/items/", response_model=List[ItemResponse])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items

@app.get("/items/{item_id}", response_model=ItemResponse)
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = crud.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.put("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item: ItemUpdate, db: Session = Depends(get_db)):
    db_item = crud.update_item(db, item_id=item_id, item=item)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    success = crud.delete_item(db, item_id=item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)