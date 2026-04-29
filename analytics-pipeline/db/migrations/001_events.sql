-- Creates the `events` table.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    store_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    session_id TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    user_ip INET NOT NULL,
    event_object_id TEXT NOT NULL,
    event_id TEXT UNIQUE NOT NULL,  -- For deduplication
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_events_store_id ON events (store_id);
CREATE INDEX idx_events_session_id ON events (session_id);
CREATE INDEX idx_events_timestamp ON events (timestamp);
