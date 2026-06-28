-- WanderAI SQLite Schema
-- Run via: python init_db.py  (or auto-created by app.py)

CREATE TABLE IF NOT EXISTS users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL,
    email      TEXT    NOT NULL UNIQUE,
    password   TEXT    NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS trips (
    trip_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    source       TEXT    DEFAULT '',
    destination  TEXT    NOT NULL,
    days         INTEGER NOT NULL,
    budget       REAL    NOT NULL,
    travelers    INTEGER DEFAULT 1,
    interests    TEXT    NOT NULL,
    travel_dates TEXT,
    itinerary    TEXT    NOT NULL,
    weather_data TEXT,
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_trips_user ON trips(user_id);
CREATE INDEX IF NOT EXISTS idx_trips_dest ON trips(destination);
