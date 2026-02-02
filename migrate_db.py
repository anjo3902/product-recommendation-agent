"""
Database Migration Script
Creates all tables defined in models.py including the users table
"""

from src.database.models import Base
from src.database.connection import engine, get_db
from sqlalchemy import inspect

def check_existing_tables():
    """Check which tables already exist"""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    return existing_tables

def migrate_database():
    """Create all tables that don't exist yet"""
    print("🔍 Checking existing tables...")
    existing_tables = check_existing_tables()
    
    if existing_tables:
        print(f"✓ Found existing tables: {', '.join(existing_tables)}")
    else:
        print("✓ No existing tables found")
    
    print("\n📦 Creating new tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("\n✅ Database migration successful!")
        
        # Check what was created
        new_tables = check_existing_tables()
        print(f"\n📋 Current tables: {', '.join(new_tables)}")
        
        # Verify users table exists
        if 'users' in new_tables:
            print("\n✓ Users table created successfully!")
            print("\nℹ️  You can now:")
            print("   1. Start the server: uvicorn main:app --reload")
            print("   2. Test endpoints at: http://localhost:8000/docs")
            print("   3. Create an account using POST /auth/signup")
        else:
            print("\n⚠️  Warning: Users table not found!")
            
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE MIGRATION SCRIPT")
    print("=" * 60)
    migrate_database()
    print("=" * 60)
