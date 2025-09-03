CREATE TABLE IF NOT EXISTS databases (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    name TEXT NOT NULL,
    format TEXT NOT NULL,
    password TEXT
);

CREATE TABLE IF NOT EXISTS users (
    id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    username TEXT,
    attempts INTEGER DEFAULT 3,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    vip INTEGER DEFAULT 0,
    refferals TEXT DEFAULT "[]"
);
