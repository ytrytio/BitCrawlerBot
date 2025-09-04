PRAGMA foreign_keys = ON;

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
    refferals TEXT DEFAULT "[]",
    hide INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS whitelist (
    id TEXT UNIQUE NOT NULL,
    username TEXT
);

CREATE TABLE IF NOT EXISTS mirrors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    token TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    owner_id TEXT REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS fsm_states (
    chat_id INTEGER,
    user_id INTEGER,
    state TEXT,
    PRIMARY KEY(chat_id, user_id)
);

CREATE TABLE IF NOT EXISTS fsm_data (
    chat_id INTEGER,
    user_id INTEGER,
    data TEXT,
    PRIMARY KEY(chat_id, user_id)
);
