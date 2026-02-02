# src/database/connection.py
"""
Database connection module for Product Recommendation System
This module provides database session management for PostgreSQL
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from src.database.models import Base
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Get database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/product_recommendation"
)

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,              # Number of permanent connections
    max_overflow=20,           # Number of temporary connections
    pool_pre_ping=True,        # Verify connections before using
    pool_recycle=3600,         # Recycle connections after 1 hour
    echo=False,                # Set to True to log SQL queries
    future=True                # Use SQLAlchemy 2.0 style
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

def get_db() -> Session:
    """
    Get database session (for FastAPI dependency injection)
    
    Usage:
        @app.get("/products")
        def get_products(db: Session = Depends(get_db)):
            products = db.query(Product).all()
            return products
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize database by creating all tables
    
    This function:
    1. Creates all tables defined in models.py
    2. Does NOT drop existing tables
    3. Is idempotent (safe to run multiple times)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info("🔧 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False

def drop_all_tables():
    """
    Drop all tables from the database
    
    ⚠️ WARNING: This will delete ALL data!
    Use only in development/testing
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.warning("⚠️  Dropping all database tables...")
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ All tables dropped successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to drop tables: {e}")
        return False

def reset_database():
    """
    Reset database (drop all tables and recreate them)
    
    ⚠️ WARNING: This will delete ALL data!
    Use only in development/testing
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.warning("⚠️  Resetting database (drop + create)...")
        drop_all_tables()
        init_db()
        logger.info("✅ Database reset complete!")
        return True
    except Exception as e:
        logger.error(f"❌ Database reset failed: {e}")
        return False

def test_connection():
    """
    Test database connection
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info("✅ Database connection successful!")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    """
    Run this module directly to initialize the database
    
    Usage:
        python -m src.database.connection
    """
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "=" * 70)
    print("DATABASE INITIALIZATION SCRIPT")
    print("=" * 70)
    print(f"\n📍 Database URL: {DATABASE_URL}")
    
    print("\n1️⃣  Testing connection...")
    if test_connection():
        print("   ✅ Connection successful!")
    else:
        print("   ❌ Connection failed! Check your DATABASE_URL")
        exit(1)
    
    print("\n2️⃣  Creating tables...")
    if init_db():
        print("   ✅ Tables created successfully!")
    else:
        print("   ❌ Table creation failed!")
        exit(1)
    
    print("\n" + "=" * 70)
    print("✅ DATABASE SETUP COMPLETE!")
    print("=" * 70)
    print("\n📋 Next steps:")
    print("   1. Run: python scripts/generate_sample_data.py")
    print("   2. Run: python scripts/verify_data.py")
    print("   3. Start your application")
    print()
