-- Creates the `daily_store_aggregates` table.

CREATE TABLE daily_store_aggregates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    store_id TEXT NOT NULL,
    date DATE NOT NULL,
    unique_users BIGINT NOT NULL DEFAULT 0,
    sessions BIGINT NOT NULL DEFAULT 0,
    page_views BIGINT NOT NULL DEFAULT 0,
    add_to_cart BIGINT NOT NULL DEFAULT 0,
    checkout_start BIGINT NOT NULL DEFAULT 0,
    checkout_success BIGINT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(store_id, date)
);

CREATE INDEX idx_daily_store_aggregates_store_id_date ON daily_store_aggregates (store_id, date);
