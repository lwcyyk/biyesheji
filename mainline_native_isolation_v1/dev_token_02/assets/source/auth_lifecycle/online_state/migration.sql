CREATE TABLE IF NOT EXISTS authority_state (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    version INTEGER NOT NULL,
    ciphertext BLOB NOT NULL
);
CREATE TABLE IF NOT EXISTS authority_events (
    version INTEGER PRIMARY KEY,
    operation TEXT NOT NULL,
    projection TEXT NOT NULL
);
PRAGMA user_version = 1;
