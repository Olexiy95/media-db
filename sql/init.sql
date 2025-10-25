PRAGMA foreign_keys = ON;

CREATE TABLE
    IF NOT EXISTS app_meta (
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_backup TIMESTAMP
    );

-- Media Table
CREATE TABLE
    media (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        rating INTEGER,
        artwork_path TEXT,
        notes TEXT,
        obtained INTEGER NOT NULL DEFAULT 0 CHECK (obtained IN (0, 1)),
        sort_title TEXT NOT NULL,
        type TEXT NOT NULL CHECK (type IN ('movie', 'show', 'music'))
    );

CREATE INDEX IF NOT EXISTS idx_media_sort ON media (sort_title COLLATE NOCASE);

-- Movie Table
CREATE TABLE
    movies (
        id TEXT PRIMARY KEY,
        media_id TEXT NOT NULL UNIQUE,
        year INTEGER CHECK (year >= 1800),
        director TEXT,
        duration INTEGER,
        FOREIGN KEY (media_id) REFERENCES media (id) ON DELETE CASCADE,
        FOREIGN KEY (director) REFERENCES directors (id) ON DELETE SET NULL
    );

CREATE TABLE
    movie_collections (id TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE);

CREATE TABLE
    show_networks (id TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE);

CREATE TABLE
    shows (
        id TEXT PRIMARY KEY,
        media_id TEXT NOT NULL UNIQUE,
        start_year INTEGER,
        end_year INTEGER,
        network TEXT,
        FOREIGN KEY (media_id) REFERENCES media (id) ON DELETE CASCADE,
        FOREIGN KEY (network) REFERENCES show_networks (id) ON DELETE SET NULL
    );

CREATE TABLE
    show_collections (id TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE);

CREATE TABLE
    show_episodes (
        id TEXT PRIMARY KEY,
        show_id TEXT NOT NULL,
        season_number INTEGER NOT NULL CHECK (season_number >= 0),
        episode_number INTEGER NOT NULL CHECK (episode_number >= 0),
        episode_name TEXT,
        FOREIGN KEY (show_id) REFERENCES shows (id) ON DELETE CASCADE,
        UNIQUE (show_id, season_number, episode_number)
    );

CREATE TABLE
    actors (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        pseudonym TEXT
    );

CREATE TABLE
    IF NOT EXISTS directors (id TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE);

CREATE UNIQUE INDEX IF NOT EXISTS ux_actors_name_nocase ON actors (name COLLATE NOCASE);

CREATE TABLE
    genres (id TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE);

CREATE UNIQUE INDEX IF NOT EXISTS ux_genres_name_nocase ON genres (name COLLATE NOCASE);

-- Relationship Join Tables
CREATE TABLE
    actor_movie_relationship (
        movie_id TEXT NOT NULL,
        actor_id TEXT NOT NULL,
        billing_order INTEGER NOT NULL CHECK (billing_order >= 1),
        FOREIGN KEY (movie_id) REFERENCES movies (id) ON DELETE CASCADE,
        FOREIGN KEY (actor_id) REFERENCES actors (id) ON DELETE RESTRICT,
        PRIMARY KEY (movie_id, actor_id)
    );

CREATE TABLE
    actor_show_relationship (
        show_id TEXT NOT NULL,
        actor_id TEXT NOT NULL,
        billing_order INTEGER NOT NULL CHECK (billing_order >= 1),
        FOREIGN KEY (show_id) REFERENCES shows (id) ON DELETE CASCADE,
        FOREIGN KEY (actor_id) REFERENCES actors (id) ON DELETE RESTRICT,
        PRIMARY KEY (show_id, actor_id)
    );

CREATE INDEX IF NOT EXISTS idx_am_actor ON actor_movie_relationship (actor_id);

CREATE TABLE
    movie_genre_relationship (
        movie_id TEXT NOT NULL,
        genre_id TEXT NOT NULL,
        FOREIGN KEY (movie_id) REFERENCES movies (id) ON DELETE CASCADE,
        FOREIGN KEY (genre_id) REFERENCES genres (id) ON DELETE RESTRICT,
        PRIMARY KEY (movie_id, genre_id)
    );

CREATE INDEX IF NOT EXISTS idx_as_actor ON actor_show_relationship (actor_id);

CREATE TABLE
    show_genre_relationship (
        show_id TEXT NOT NULL,
        genre_id TEXT NOT NULL,
        FOREIGN KEY (show_id) REFERENCES shows (id) ON DELETE CASCADE,
        FOREIGN KEY (genre_id) REFERENCES genres (id) ON DELETE RESTRICT,
        PRIMARY KEY (show_id, genre_id)
    );

CREATE TABLE
    movie_collection_relationship (
        movie_id TEXT NOT NULL,
        collection_id TEXT NOT NULL,
        FOREIGN KEY (movie_id) REFERENCES movies (id) ON DELETE CASCADE,
        FOREIGN KEY (collection_id) REFERENCES movie_collections (id) ON DELETE RESTRICT,
        PRIMARY KEY (movie_id, collection_id)
    );

CREATE TABLE
    show_collection_relationship (
        show_id TEXT NOT NULL,
        collection_id TEXT NOT NULL,
        FOREIGN KEY (show_id) REFERENCES shows (id) ON DELETE CASCADE,
        FOREIGN KEY (collection_id) REFERENCES show_collections (id) ON DELETE RESTRICT,
        PRIMARY KEY (show_id, collection_id)
    );