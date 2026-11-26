-- V1 remains immutable for existing Flyway installations. Preserve legacy rows
-- in an unexposed historical table; no tenant/store relationship enters the catalog.
ALTER TABLE stores RENAME TO legacy_stores;
CREATE TABLE products (
 id UUID PRIMARY KEY,
 slug VARCHAR(80) NOT NULL UNIQUE CHECK (slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
 name VARCHAR(160) NOT NULL CHECK(length(trim(name)) > 0),
 description VARCHAR(2000) NOT NULL,
 price NUMERIC(12,2) NOT NULL CHECK(price > 0),
 category VARCHAR(80) NOT NULL CHECK(length(trim(category)) > 0),
 image_path VARCHAR(255), featured BOOLEAN NOT NULL DEFAULT FALSE,
 availability VARCHAR(32) NOT NULL CHECK(availability IN ('AVAILABLE','TEMPORARILY_UNAVAILABLE','DISCONTINUED','ARCHIVED')),
 created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
 updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
