-- Gate 2: Store inference capabilities
CREATE TABLE IF NOT EXISTS app.inference_capabilities (
    id UUID PRIMARY KEY,
    vcv_data JSONB NOT NULL,
    harvested_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_vcv_harvested ON app.inference_capabilities(harvested_at DESC);
