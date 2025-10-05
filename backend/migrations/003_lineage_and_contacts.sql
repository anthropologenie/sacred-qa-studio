-- Migration 003: Add lineage and contacts tracking

-- Sacred Contacts: API request logging
CREATE TABLE IF NOT EXISTS app.sacred_contacts (
    contact_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_payload JSONB NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    client_identity VARCHAR(255),
    api_endpoint VARCHAR(255) NOT NULL,
    status_code INTEGER,
    response_payload JSONB
);

CREATE INDEX idx_contact_timestamp ON app.sacred_contacts(timestamp DESC);
CREATE INDEX idx_contact_endpoint ON app.sacred_contacts(api_endpoint);

-- Request Lineage: Agent call tree
CREATE TABLE IF NOT EXISTS app.request_lineage (
    lineage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_lineage_id UUID REFERENCES app.request_lineage(lineage_id),
    agent_name VARCHAR(100) NOT NULL,
    operation_type VARCHAR(100) NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB,
    duration_ms INTEGER,
    success BOOLEAN DEFAULT true
);

CREATE INDEX idx_lineage_parent ON app.request_lineage(parent_lineage_id);
CREATE INDEX idx_lineage_timestamp ON app.request_lineage(timestamp DESC);
