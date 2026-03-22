-- Database initialization for Network Monitor
-- This script runs when PostgreSQL container starts

-- Create tables
CREATE TABLE IF NOT EXISTS services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    url VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'unknown',
    response_time FLOAT,
    last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS network_events (
    id SERIAL PRIMARY KEY,
    source_service VARCHAR(100),
    target_service VARCHAR(100),
    event_type VARCHAR(50),
    data JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_services_name ON services(name);
CREATE INDEX IF NOT EXISTS idx_network_events_timestamp ON network_events(timestamp DESC);

-- Create view for service status
CREATE OR REPLACE VIEW service_status AS
SELECT 
    s.id,
    s.name,
    s.url,
    s.status,
    s.response_time,
    s.last_check,
    s.created_at
FROM services s
ORDER BY s.name;
