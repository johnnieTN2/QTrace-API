import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

def get_database_url():
    """Get database URL from Railway environment variables"""
    
    # First try Railway's automatic DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if database_url and database_url != "None" and "localhost" not in database_url:
        print(f"Using DATABASE_URL: {database_url[:20]}...")
        return database_url
    
    # Construct from individual variables
    pghost = os.getenv("PGHOST")
    pgport = os.getenv("PGPORT", "5432")
    pgdatabase = os.getenv("PGDATABASE")
    pguser = os.getenv("PGUSER")
    pgpassword = os.getenv("PGPASSWORD")
    
    print(f"Environment check - PGHOST: {pghost}, PGDATABASE: {pgdatabase}")
    
    # Check if we have Railway variables
    if all([pghost, pgdatabase, pguser, pgpassword]) and pghost != "None":
        url = f"postgresql://{pguser}:{pgpassword}@{pghost}:{pgport}/{pgdatabase}"
        print(f"Using constructed URL with host: {pghost}")
        return url
    
    # This should not happen in Railway
    print("⚠️ WARNING: No Railway database variables found!")
    return "postgresql://postgres:password@localhost:5432/qtrace"

DATABASE_URL = get_database_url()

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    print("✅ Database engine created successfully")
except Exception as e:
    print(f"❌ Database engine creation failed: {e}")
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
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        raise