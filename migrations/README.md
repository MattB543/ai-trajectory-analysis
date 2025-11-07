# Database Migrations

This folder contains SQL migration files for the AI Trajectory Analysis database.

## Setup Instructions

### 1. Create the Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE ai_trajectories;

# Connect to the new database
\c ai_trajectories

# Enable pgvector extension (if needed later)
CREATE EXTENSION IF NOT EXISTS vector;
```

### 2. Run Initial Schema

```bash
# From the project root
psql -U postgres -d ai_trajectories -f schema.sql
```

### 3. Run Migration 001

```bash
# Add full content columns
psql -U postgres -d ai_trajectories -f migrations/001_add_full_content.sql
```

## Verify Schema

```sql
-- Check the trajectories table structure
\d trajectories

-- Should show columns:
-- id, title, authors, year, scenario_lane, multi_scenario, rating,
-- why_it_matters, links, created_at, updated_at,
-- part_number, part_name, file_name, full_content
```

## Load Documents

After running the migrations, load all documents:

```bash
# Set database password (if needed)
export POSTGRES_PASSWORD=your_password

# Run the loading script
python scripts/load_full_documents.py
```

## Connection Info

Default connection parameters (edit in script if different):
- **Database:** ai_trajectories
- **User:** postgres
- **Password:** postgres (or set POSTGRES_PASSWORD env var)
- **Host:** localhost
- **Port:** 5432
