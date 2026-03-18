BEGIN;

ALTER TABLE findings
    ADD COLUMN IF NOT EXISTS file_path TEXT,
    ADD COLUMN IF NOT EXISTS line INTEGER,
    ADD COLUMN IF NOT EXISTS remediation TEXT;

CREATE TABLE IF NOT EXISTS policy_evaluations (
    id BIGSERIAL PRIMARY KEY,
    server_name TEXT NOT NULL,
    server_version TEXT,
    bundle_name TEXT NOT NULL,
    bundle_version INTEGER NOT NULL,
    decision TEXT NOT NULL,
    runtime_profile TEXT NOT NULL,
    remote_access TEXT NOT NULL,
    require_digest_pin BOOLEAN NOT NULL DEFAULT FALSE,
    matched_rules JSONB NOT NULL DEFAULT '[]'::JSONB,
    reasons JSONB NOT NULL DEFAULT '[]'::JSONB,
    recommended_actions JSONB NOT NULL DEFAULT '[]'::JSONB,
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_policy_evaluations_server_name ON policy_evaluations (server_name, evaluated_at DESC);

COMMIT;
