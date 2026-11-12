CREATE TABLE IF NOT EXISTS vehicles (
    id BIGSERIAL PRIMARY KEY,
    plate VARCHAR(8) NOT NULL UNIQUE,
    owner_name VARCHAR(120) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS access_events (
    event_id VARCHAR(24) PRIMARY KEY,
    vehicle_id BIGINT REFERENCES vehicles(id),
    plate VARCHAR(8) NOT NULL,
    event_type VARCHAR(5) NOT NULL CHECK (event_type IN ('ENTRY', 'EXIT')),
    gate_id VARCHAR(64) NOT NULL,
    authorized BOOLEAN NOT NULL DEFAULT FALSE,
    evidence_key VARCHAR(512),
    occurred_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS access_events_plate_occurred_idx
    ON access_events (plate, occurred_at DESC);
