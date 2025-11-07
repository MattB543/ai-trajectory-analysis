-- Migration: Add full document content storage
-- Created: 2025-10-11
-- Purpose: Add columns to trajectories table to store full markdown content
--          and handle multi-part/multi-scenario documents
-- This file was created as a direct request from the user

-- Add columns for full content and part tracking
ALTER TABLE trajectories
ADD COLUMN part_number INTEGER DEFAULT 1,
ADD COLUMN part_name TEXT,
ADD COLUMN file_name TEXT,
ADD COLUMN full_content TEXT;

-- Add comment to explain the new columns
COMMENT ON COLUMN trajectories.part_number IS 'Part number for multi-part documents (1 for single docs)';
COMMENT ON COLUMN trajectories.part_name IS 'Name of the part/scenario (e.g., "Part I", "arms_race", NULL for single docs)';
COMMENT ON COLUMN trajectories.file_name IS 'Source markdown file name (e.g., "full_doc.md", "arms_race.md")';
COMMENT ON COLUMN trajectories.full_content IS 'Complete markdown content of the document/part';

-- Create index for searching across full content
CREATE INDEX idx_trajectories_full_content_search ON trajectories USING gin(to_tsvector('english', full_content));

-- Update the unique constraint to allow multiple parts per title
-- (We'll handle uniqueness at the application level for now)
