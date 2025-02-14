CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE entries(
    id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    date DATETIME,
    time TEXT,
    duration TEXT,
    user_id INTEGER REFERENCES users
);