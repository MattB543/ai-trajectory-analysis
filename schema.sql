-- AI Trajectory Analysis Database Schema
-- PostgreSQL schema for storing trajectory metadata and content chunks

-- Main trajectories metadata table
CREATE TABLE trajectories (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    authors TEXT,
    year INTEGER,
    scenario_lane TEXT,
    multi_scenario BOOLEAN,
    rating INTEGER,
    why_it_matters TEXT,
    links TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Content chunks table
CREATE TABLE trajectory_chunks (
    id SERIAL PRIMARY KEY,
    trajectory_id INTEGER NOT NULL REFERENCES trajectories(id) ON DELETE CASCADE,
    chunk_order INTEGER NOT NULL,  -- Position within the document
    section_title TEXT,             -- Section/page heading if available
    content TEXT NOT NULL,          -- The actual chunk text
    chunk_metadata JSONB,           -- Flexible field for page numbers, word count, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_trajectory_chunk UNIQUE(trajectory_id, chunk_order)
);

-- Indexes for performance
CREATE INDEX idx_trajectory_chunks_trajectory_id ON trajectory_chunks(trajectory_id);
CREATE INDEX idx_trajectory_chunks_content_search ON trajectory_chunks USING gin(to_tsvector('english', content));
CREATE INDEX idx_trajectories_year ON trajectories(year);
CREATE INDEX idx_trajectories_rating ON trajectories(rating);
