-- Creates the `sessions` and `user_identities` tables.

CREATE TABLE user_identities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_ip INET NOT NULL UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_identity_id UUID NOT NULL REFERENCES user_identities(id),
    session_id TEXT NOT NULL,
    store_id TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(session_id, store_id)
);

CREATE INDEX idx_sessions_user_identity_id ON sessions (user_identity_id);
CREATE INDEX idx_sessions_session_id ON sessions (session_id);
