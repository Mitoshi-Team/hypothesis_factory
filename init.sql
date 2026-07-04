-- Initial schema for Hypothesis Factory.
-- Postgres executes this file on first startup via /docker-entrypoint-initdb.d.

CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(50) PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sessions (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL DEFAULT '',
    constraints TEXT,
    weights JSONB,
    status VARCHAR(50) NOT NULL DEFAULT 'created',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);

CREATE TABLE IF NOT EXISTS messages (
    id VARCHAR(50) PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    content TEXT NOT NULL DEFAULT '',
    iteration INT NOT NULL DEFAULT 0,
    status VARCHAR(50) NOT NULL DEFAULT 'queued',
    task_id VARCHAR(100) DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);

CREATE TABLE IF NOT EXISTS files (
    id VARCHAR(50) PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    message_id VARCHAR(50) REFERENCES messages(id) ON DELETE SET NULL,
    original_name VARCHAR(255) NOT NULL DEFAULT '',
    storage_path VARCHAR(512) NOT NULL,
    mime_type VARCHAR(100) NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_files_session_id ON files(session_id);
CREATE INDEX IF NOT EXISTS idx_files_message_id ON files(message_id);

CREATE TABLE IF NOT EXISTS ner_entities (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    entity_id VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    label VARCHAR(100) NOT NULL,
    source_file VARCHAR(255) DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ner_entities_session_id ON ner_entities(session_id);

CREATE TABLE IF NOT EXISTS pipeline_results (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    message_id VARCHAR(50) NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    hypothesis_json TEXT NOT NULL DEFAULT '',
    review_json TEXT NOT NULL DEFAULT '',
    graph_json TEXT NOT NULL DEFAULT '',
    trace_json TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pipeline_results_session_id ON pipeline_results(session_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_results_message_id ON pipeline_results(message_id);
