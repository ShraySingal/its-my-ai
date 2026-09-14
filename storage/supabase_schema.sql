-- ====================================================================
-- IT'S MY AI — Complete PostgreSQL & pgvector Database Schema
-- Implements Sections 8, 9, and 39 of ITS_MY_AI_Master_Prompt.pdf
-- Run this script directly in the Supabase SQL Editor (https://supabase.com)
-- ====================================================================

-- 1. Enable pgvector extension for long-term semantic vector memory
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==========================================
-- 2. TABLE: memories (Long-Term Memory & Vector Store)
-- ==========================================
CREATE TABLE IF NOT EXISTS public.memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    category TEXT DEFAULT 'fact',            -- fact, preference, routine, context
    tags TEXT[] DEFAULT '{}',
    embedding vector(1536),                  -- Supports OpenAI / Gemini 1536/768 embeddings
    is_sensitive BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_memories_category ON public.memories(category);
CREATE INDEX IF NOT EXISTS idx_memories_created_at ON public.memories(created_at DESC);

-- ==========================================
-- 3. TABLE: devices (Multi-Device Command Center Registry)
-- ==========================================
CREATE TABLE IF NOT EXISTS public.devices (
    id TEXT PRIMARY KEY,                     -- e.g., 'laptop-command-center', 'android-mobile-01'
    name TEXT NOT NULL,
    type TEXT NOT NULL,                      -- Laptop, Mobile, Tablet, IoT, Workstation
    status TEXT DEFAULT 'offline',           -- online, offline, idle, sleeping
    ip_address TEXT,
    battery_percent INTEGER,
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    authorized BOOLEAN DEFAULT TRUE,
    capabilities JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==========================================
-- 4. TABLE: todos (Persistent Task Management)
-- ==========================================
CREATE TABLE IF NOT EXISTS public.todos (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT DEFAULT 'general',
    priority TEXT DEFAULT 'medium',          -- low, medium, high, urgent
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_todos_completed ON public.todos(completed);

-- ==========================================
-- 5. TABLE: audit_logs (Structured Security & Tool Audit Trail)
-- ==========================================
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    event_type TEXT NOT NULL,                -- tool_execution, confirmation, denied_action, security_alert
    action TEXT NOT NULL,
    status TEXT NOT NULL,                    -- success, error, blocked, awaiting_confirmation
    user_or_device TEXT NOT NULL,
    permission_level INTEGER,                -- 1, 2, 3, 4
    details JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON public.audit_logs(timestamp DESC);

-- ==========================================
-- 6. Storage Buckets Setup (Supabase Storage)
-- Prepares the standard object storage buckets:
-- /documents, /images, /projects, /audio, /hologram, /backups
-- ==========================================
INSERT INTO storage.buckets (id, name, public) 
VALUES 
    ('documents', 'documents', false),
    ('images', 'images', false),
    ('projects', 'projects', false),
    ('audio', 'audio', false),
    ('hologram', 'hologram', true),
    ('backups', 'backups', false)
ON CONFLICT (id) DO NOTHING;

-- ==========================================
-- 7. Row Level Security (RLS) Policies
-- ==========================================
ALTER TABLE public.memories ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.todos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

-- Allow service role full access
CREATE POLICY "Service Role Full Access Memories" ON public.memories FOR ALL USING (true);
CREATE POLICY "Service Role Full Access Devices" ON public.devices FOR ALL USING (true);
CREATE POLICY "Service Role Full Access Todos" ON public.todos FOR ALL USING (true);
CREATE POLICY "Service Role Full Access Audit" ON public.audit_logs FOR ALL USING (true);
