# PostgreSQL Setup Guide
# Product Recommendation System - Database Configuration

## 📋 Prerequisites

1. **PostgreSQL 14 or higher** installed on your system
2. **Python 3.9+** with pip
3. **pgAdmin** (optional, for GUI management)

---

## 🚀 Step-by-Step Setup

### Step 1: Install PostgreSQL

#### Windows:
1. Download from: https://www.postgresql.org/download/windows/
2. Run the installer (EDB installer recommended)
3. During installation:
   - Set password for `postgres` user (remember this!)
   - Default port: 5432
   - Select "PostgreSQL Server" and "pgAdmin"
4. Verify installation:
   ```powershell
   psql --version
   ```

#### Alternative - Using Docker:
```bash
docker run --name postgres-db -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:14
```

---

### Step 2: Create Database

#### Option A: Using psql (Command Line)
```powershell
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE product_recommendation;

# Verify
\l

# Exit
\q
```

#### Option B: Using pgAdmin (GUI)
1. Open pgAdmin
2. Right-click on "Databases" → "Create" → "Database"
3. Name: `product_recommendation`
4. Owner: `postgres`
5. Click "Save"

---

### Step 3: Install Python Dependencies

```powershell
# Install required packages
pip install sqlalchemy psycopg2-binary python-dotenv
```

**Package Details:**
- `sqlalchemy`: ORM for database operations
- `psycopg2-binary`: PostgreSQL adapter for Python
- `python-dotenv`: Load environment variables from .env

---

### Step 4: Configure Environment Variables

Create `.env` file in project root:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/product_recommendation

# Alternative formats:
# With different user:
# DATABASE_URL=postgresql://username:password@localhost:5432/product_recommendation

# With remote database:
# DATABASE_URL=postgresql://user:pass@remote-host:5432/dbname

# Application Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
```

**Important Notes:**
- Replace `your_password` with your actual PostgreSQL password
- Never commit `.env` file to Git (add to `.gitignore`)

---

### Step 5: Initialize Database Tables

Run the database initialization script:

```powershell
# Method 1: Using the connection module
python -m src.database.connection

# Method 2: Using session module (if preferred)
python src/database/session.py
```

**Expected Output:**
```
======================================================================
DATABASE INITIALIZATION SCRIPT
======================================================================

📍 Database URL: postgresql://postgres:***@localhost:5432/product_recommendation

1️⃣  Testing connection...
   ✅ Connection successful!

2️⃣  Creating tables...
   ✅ Tables created successfully!

======================================================================
✅ DATABASE SETUP COMPLETE!
======================================================================
```

---

### Step 6: Verify Tables Created

```powershell
# Connect to database
psql -U postgres -d product_recommendation

# List all tables
\dt

# Expected output:
#  Schema |       Name        | Type  |  Owner
# --------+-------------------+-------+----------
#  public | products          | table | postgres
#  public | reviews           | table | postgres
#  public | price_history     | table | postgres
#  public | users             | table | postgres
#  ...

# View table structure
\d products

# Exit
\q
```

---

### Step 7: Generate Sample Data

```powershell
# Generate comprehensive dataset (600-720 products)
python scripts/generate_sample_data.py
```

**Expected Output:**
```
🎯 Starting realistic data generation...
======================================================================

📦 Category: Electronics
  └─ Subcategory: Headphones
  └─ Subcategory: Smartphones
  └─ Subcategory: Laptops
  ...

======================================================================
✅ REALISTIC DATA GENERATION COMPLETE!
======================================================================
📊 Total Products:         652
⭐ Total Reviews:          9,128
💰 Price History Records:  59,332
📈 Avg Reviews/Product:    14.0
📂 Total Categories:       14
📁 Total Subcategories:    62
======================================================================
```

---

### Step 8: Verify Data

```powershell
# Run verification script
python scripts/verify_data.py
```

**Expected Output:**
```
🔍 DATA QUALITY VERIFICATION
======================================================================

✅ Total Products: 652
✅ Products with Reviews: 652 (100.0%)
✅ Products In Stock: 489 (75.0%)

⭐ Total Reviews: 9,128
✅ Verified Reviews: 6,846 (75.0%)

📊 Rating Distribution:
  5⭐:  2,738 ████████████████████████
  4⭐:  2,738 ████████████████████████
  3⭐:  1,826 ████████████████
  2⭐:  1,369 ████████████
  1⭐:   457 ████

💰 Total Price History Records: 59,332
📈 Average records per product: 91.0

======================================================================
✅ DATA QUALITY VERIFICATION COMPLETE!
🎉 Data is ready for production testing!
```

---

## 📊 Database Schema

### Main Tables:

1. **products** (652 rows)
   - Product details, pricing, ratings
   - Subcategory for better organization
   - JSON fields for features and specifications

2. **reviews** (~9,128 rows)
   - User reviews with ratings
   - Verified purchase flags
   - Helpful counts

3. **price_history** (~59,332 rows)
   - 90-day price tracking per product
   - Historical price data for trends

4. **users**
   - User authentication data
   - Profile information

---

## 🔧 Useful PostgreSQL Commands

### Database Management:
```sql
-- List all databases
\l

-- Connect to database
\c product_recommendation

-- List tables
\dt

-- View table structure
\d products

-- View table data
SELECT * FROM products LIMIT 10;

-- Count records
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM reviews;
SELECT COUNT(*) FROM price_history;

-- Check data by category
SELECT category, COUNT(*) FROM products GROUP BY category;

-- View products with reviews
SELECT p.name, p.price, p.rating, COUNT(r.id) as review_count
FROM products p
LEFT JOIN reviews r ON p.id = r.product_id
GROUP BY p.id
LIMIT 10;
```

### Performance Queries:
```sql
-- Create indexes for better performance
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_subcategory ON products(subcategory);
CREATE INDEX idx_products_brand ON products(brand);
CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_reviews_product_id ON reviews(product_id);
CREATE INDEX idx_price_history_product_id ON price_history(product_id);

-- View index usage
SELECT * FROM pg_stat_user_indexes;
```

---

## 🛠️ Troubleshooting

### Issue 1: "psql: FATAL: password authentication failed"
**Solution:**
```powershell
# Reset password
psql -U postgres
ALTER USER postgres WITH PASSWORD 'new_password';
```

### Issue 2: "Connection refused" or "Could not connect to server"
**Solution:**
- Check if PostgreSQL service is running:
  ```powershell
  # Windows Services
  services.msc
  # Look for "postgresql-x64-14" and start if stopped
  ```

### Issue 3: "database does not exist"
**Solution:**
```powershell
psql -U postgres
CREATE DATABASE product_recommendation;
\q
```

### Issue 4: Import Error - "No module named 'psycopg2'"
**Solution:**
```powershell
pip install psycopg2-binary
```

### Issue 5: SQLAlchemy connection string format error
**Solution:**
```
Old format: postgresql://user:pass@host/db
New format: postgresql+psycopg2://user:pass@host/db

Update .env:
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/product_recommendation
```

---

## 🔐 Security Best Practices

1. **Never commit .env file**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Use strong passwords**
   - Minimum 12 characters
   - Mix of letters, numbers, symbols

3. **Limit database user permissions**
   ```sql
   CREATE USER app_user WITH PASSWORD 'strong_password';
   GRANT CONNECT ON DATABASE product_recommendation TO app_user;
   GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
   ```

4. **Enable SSL for production**
   ```env
   DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
   ```

---

## 📈 Performance Optimization

### 1. Connection Pooling (Already configured)
```python
# src/database/connection.py
pool_size=10          # 10 permanent connections
max_overflow=20       # 20 additional temporary connections
pool_recycle=3600     # Recycle after 1 hour
```

### 2. Query Optimization
```python
# Use eager loading for relationships
products = db.query(Product).options(
    joinedload(Product.reviews),
    joinedload(Product.price_history)
).all()
```

### 3. Batch Operations
```python
# Insert multiple records at once (already done in generate_sample_data.py)
db.bulk_insert_mappings(Product, product_list)
db.commit()
```

---

## 🎯 Next Steps

1. ✅ PostgreSQL installed
2. ✅ Database created
3. ✅ Tables initialized
4. ✅ Sample data generated
5. ⏭️ **Implement caching (Phase 1.5)** - 17x performance boost
6. ⏭️ **Build agents (Phase 2-7)** - Use this data for testing
7. ⏭️ **Run evaluation (Phase 9)** - Measure quality

---

## 📚 Additional Resources

- PostgreSQL Documentation: https://www.postgresql.org/docs/
- SQLAlchemy Docs: https://docs.sqlalchemy.org/
- pgAdmin: https://www.pgadmin.org/
- Database GUI: DBeaver, DataGrip, or TablePlus

---

## 💡 Pro Tips

1. **Backup your database regularly**
   ```powershell
   pg_dump -U postgres product_recommendation > backup.sql
   ```

2. **Restore from backup**
   ```powershell
   psql -U postgres product_recommendation < backup.sql
   ```

3. **Monitor database size**
   ```sql
   SELECT pg_size_pretty(pg_database_size('product_recommendation'));
   ```

4. **View active connections**
   ```sql
   SELECT * FROM pg_stat_activity WHERE datname = 'product_recommendation';
   ```

---

🎉 **You're all set! Your PostgreSQL database is ready for the Product Recommendation System!**
