-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

-- Entries table
CREATE TABLE entries (
    id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    date DATETIME,
    time TEXT,
    duration TEXT,
    user_id INTEGER REFERENCES users,
    category_id INTEGER DEFAULT 1 REFERENCES categories ON DELETE SET DEFAULT
);

-- Categories table
CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE
);

-- Groups table
CREATE TABLE groups (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    description TEXT
);

-- Roles table
CREATE TABLE roles (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE CHECK(name IN ('admin', 'moderator', 'member'))
);


-- Many-to-many relationship between entries and groups
CREATE TABLE entry_groups (
    entry_id INTEGER REFERENCES entries ON DELETE CASCADE,
    group_id INTEGER REFERENCES groups ON DELETE CASCADE,
    PRIMARY KEY (entry_id, group_id)
);

-- Many-to-many relationship between users and groups
CREATE TABLE user_groups (
    user_id INTEGER REFERENCES users ON DELETE CASCADE,
    group_id INTEGER REFERENCES groups ON DELETE CASCADE,
    role_id INTEGER REFERENCES roles ON DELETE SET NULL,
    PRIMARY KEY (user_id, group_id)
);


-- User RSVPs to entries
CREATE TABLE entry_rsvps (
    user_id INTEGER REFERENCES users ON DELETE CASCADE,
    entry_id INTEGER REFERENCES entries ON DELETE CASCADE,
    status TEXT CHECK(status IN ('attending', 'maybe', 'declined')) NOT NULL DEFAULT 'declined',
    PRIMARY KEY (user_id, entry_id)
);

-- Create default category
INSERT INTO categories (id, name) VALUES (1, 'Uncategorized')
ON CONFLICT (id) DO NOTHING;
