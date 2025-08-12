import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

def get_database_url():
    """Get database URL from Railway environment variables with fallbacks"""
    
    # First try Railway's automatic DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if database_url and database_url != "None":
        return database_url
    
    # If not available, construct from individual variables
    pghost = os.getenv("PGHOST")
    pgport = os.getenv("PGPORT", "5432")
    pgdatabase = os.getenv("PGDATABASE")
    pguser = os.getenv("PGUSER")
    pgpassword = os.getenv("PGPASSWORD")
    
    # Check if we have all required variables
    if all([pghost, pgdatabase, pguser, pgpassword]) and pghost != "None":
        return f"postgresql://{pguser}:{pgpassword}@{pghost}:{pgport}/{pgdatabase}"
    
    # Fallback for local development
    return "postgresql://postgres:password@localhost:5432/qtrace"

DATABASE_URL = get_database_url()
print(f"Connecting to database: {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
except Exception as e:
    print(f"Database connection error: {e}")
    raise

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    """Test the database connection"""
    try:
        with engine.connect() as connection:
            print("✅ Database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def create_tables():
    """Create all tables"""
    try:
        from .models import Item  # Import here to avoid circular imports
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        raise