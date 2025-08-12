from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Railway provides these automatically when services are in same project
PGHOST = os.getenv("PGHOST")
PGPORT = os.getenv("PGPORT")
PGDATABASE = os.getenv("PGDATABASE")
PGUSER = os.getenv("PGUSER")
PGPASSWORD = os.getenv("PGPASSWORD")

# Get database URL from environment variables
DATABASE_URL = f"postgresql://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


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