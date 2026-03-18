BEGIN;

CREATE TABLE registries (
    id BIGSERIAL PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    base_url TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE servers (
    id BIGSERIAL PRIMARY KEY,
    registry_id BIGINT NOT NULL REFERENCES registries(id) ON DELETE CASCADE,
    canonical_name TEXT NOT NULL,
    display_name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    website_url TEXT,
    repository_url TEXT,
    repository_source TEXT,
    repository_id TEXT,
    repository_subfolder TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (registry_id, canonical_name)
);

CREATE TABLE server_versions (
    id BIGSERIAL PRIMARY KEY,
    server_id BIGINT NOT NULL REFERENCES servers(id) ON DELETE CASCADE,
    version TEXT NOT NULL,
    schema_url TEXT,
    published_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'active',
    is_latest BOOLEAN NOT NULL DEFAULT FALSE,
    raw_document JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (server_id, version)
);

CREATE TABLE server_transports (
    id BIGSERIAL PRIMARY KEY,
    server_version_id BIGINT NOT NULL REFERENCES server_versions(id) ON DELETE CASCADE,
    transport_type TEXT NOT NULL,
    endpoint_url TEXT,
    headers JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE package_artifacts (
    id BIGSERIAL PRIMARY KEY,
    server_version_id BIGINT NOT NULL REFERENCES server_versions(id) ON DELETE CASCADE,
    package_type TEXT NOT NULL,
    package_ref TEXT NOT NULL,
    digest TEXT,
    provenance JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE scan_runs (
    id BIGSERIAL PRIMARY KEY,
    server_version_id BIGINT NOT NULL REFERENCES server_versions(id) ON DELETE CASCADE,
    scanner_name TEXT NOT NULL,
    scanner_version TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    summary JSONB NOT NULL DEFAULT '{}'::JSONB
);

CREATE TABLE findings (
    id BIGSERIAL PRIMARY KEY,
    scan_run_id BIGINT NOT NULL REFERENCES scan_runs(id) ON DELETE CASCADE,
    finding_key TEXT NOT NULL,
    severity TEXT NOT NULL,
    confidence TEXT NOT NULL,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    detail TEXT NOT NULL,
    evidence JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE risk_scores (
    id BIGSERIAL PRIMARY KEY,
    server_version_id BIGINT NOT NULL REFERENCES server_versions(id) ON DELETE CASCADE,
    score NUMERIC(5,2) NOT NULL,
    decision_class TEXT NOT NULL,
    evidence_count INTEGER NOT NULL DEFAULT 0,
    score_breakdown JSONB NOT NULL DEFAULT '{}'::JSONB,
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (server_version_id)
);

CREATE TABLE policy_bundles (
    id BIGSERIAL PRIMARY KEY,
    bundle_name TEXT NOT NULL,
    bundle_version INTEGER NOT NULL,
    source_path TEXT,
    sha256 TEXT NOT NULL,
    document JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (bundle_name, bundle_version)
);

CREATE TABLE audit_events (
    id BIGSERIAL PRIMARY KEY,
    event_type TEXT NOT NULL,
    actor TEXT,
    server_name TEXT,
    server_version TEXT,
    policy_bundle_name TEXT,
    policy_bundle_version INTEGER,
    decision TEXT,
    event_data JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_server_versions_server_latest ON server_versions (server_id, is_latest);
CREATE INDEX idx_transports_server_version ON server_transports (server_version_id);
CREATE INDEX idx_scan_runs_server_version ON scan_runs (server_version_id, started_at DESC);
CREATE INDEX idx_findings_scan_run ON findings (scan_run_id);
CREATE INDEX idx_risk_scores_class ON risk_scores (decision_class, score DESC);
CREATE INDEX idx_audit_events_created_at ON audit_events (created_at DESC);

COMMIT;
