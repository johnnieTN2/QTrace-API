from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# If DATABASE_URL is not set, try to build it from individual components
if not DATABASE_URL:
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    
    if all([db_host, db_name, db_user, db_password]):
        DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        print(f"✅ Built DATABASE_URL from individual components")
    else:
        missing = [var for var, val in [
            ("DB_HOST", db_host), ("DB_NAME", db_name), 
            ("DB_USER", db_user), ("DB_PASSWORD", db_password)
        ] if not val]
        print(f"❌ Missing required environment variables: {missing}")

# Debug: Print what we found (hide password for security)
if DATABASE_URL:
    safe_url = DATABASE_URL
    if "@" in safe_url and ":" in safe_url:
        # Hide password in URL for logging
        parts = safe_url.split("@")
        if ":" in parts[0]:
            user_pass = parts[0].split("://")[1]
            if ":" in user_pass:
                user = user_pass.split(":")[0]
                safe_url = safe_url.replace(user_pass, f"{user}:****")
    print(f"DEBUG: DATABASE_URL = {safe_url}")
else:
    print("DEBUG: DATABASE_URL = None")

print(f"DEBUG: Current working directory = {os.getcwd()}")
print(f"DEBUG: .env file exists = {os.path.exists('.env')}")

# For Railway PostgreSQL, the URL might come in a format that needs adjustment for SQLAlchemy
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Only create engine if DATABASE_URL is available
if DATABASE_URL:
    # Create SQLAlchemy engine
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,  # Recycle connections every hour
        echo=False  # Set to True for SQL query logging during development
    )
else:
    print("❌ No DATABASE_URL found! Please check your .env file.")
    engine = None

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None

# Create Base class for our models
Base = declarative_base()

# Dependency to get database session
def get_db():
    """
    Database session dependency for FastAPI endpoints.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to test database connection
def test_connection():
    """
    Test the database connection.
    Returns True if connection is successful, False otherwise.
    """
    if not engine:
        print("❌ No database engine available. Check your DATABASE_URL.")
        return False
        
    try:
        # Try to create a connection with proper SQLAlchemy 2.0 syntax
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

# Function to create all tables
def create_tables():
    """
    Create all tables in the database.
    Should be called after all models are defined.
    """
    if not engine:
        print("❌ No database engine available. Check your DATABASE_URL.")
        return False
        
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False