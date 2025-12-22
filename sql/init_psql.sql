CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS citext;

CREATE OR REPLACE FUNCTION nanoid(len integer DEFAULT 10)
RETURNS text
LANGUAGE plpgsql
AS $$
DECLARE
  alphabet constant text := '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
  out text := '';
  b integer;
BEGIN
  WHILE length(out) < len LOOP
    b := get_byte(gen_random_bytes(1), 0);
    IF b < 248 THEN
      out := out || substr(alphabet, (b % 62) + 1, 1);
    END IF;
  END LOOP;
  RETURN out;
END;
$$;

CREATE TABLE app_meta (
  last_updated TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_backup  TIMESTAMPTZ
);

CREATE TABLE directors (
  id   TEXT PRIMARY KEY DEFAULT nanoid(10),
  name CITEXT NOT NULL UNIQUE
);

CREATE TABLE media (
  id           TEXT PRIMARY KEY DEFAULT nanoid(10),
  title        TEXT NOT NULL,
  rating       INTEGER,
  artwork_path TEXT,
  notes        TEXT,
  obtained     BOOLEAN NOT NULL DEFAULT FALSE,
  sort_title   TEXT NOT NULL,
  type         TEXT NOT NULL CHECK (type IN ('movie', 'show', 'music'))
);

CREATE INDEX idx_media_sort ON media (sort_title);
CREATE INDEX idx_media_type ON media (type);
CREATE INDEX idx_media_obtained ON media (obtained);

CREATE TABLE movies (
  id        TEXT PRIMARY KEY DEFAULT nanoid(10),
  media_id  TEXT NOT NULL UNIQUE,
  year      INTEGER CHECK (year >= 1800),
  director  TEXT,
  duration  INTEGER,
  FOREIGN KEY (media_id) REFERENCES media (id) ON DELETE CASCADE,
  FOREIGN KEY (director) REFERENCES directors (id) ON DELETE SET NULL
);

CREATE INDEX idx_movies_media_id ON movies (media_id);
CREATE INDEX idx_movies_director ON movies (director);
CREATE INDEX idx_movies_year ON movies (year);

CREATE TABLE movie_collections (
  id   TEXT PRIMARY KEY DEFAULT nanoid(10),
  name CITEXT NOT NULL UNIQUE
);

CREATE TABLE show_networks (
  id   TEXT PRIMARY KEY DEFAULT nanoid(10),
  name CITEXT NOT NULL UNIQUE
);

CREATE TABLE shows (
  id         TEXT PRIMARY KEY DEFAULT nanoid(10),
  media_id   TEXT NOT NULL UNIQUE,
  start_year INTEGER,
  end_year   INTEGER,
  network    TEXT,
  FOREIGN KEY (media_id) REFERENCES media (id) ON DELETE CASCADE,
  FOREIGN KEY (network) REFERENCES show_networks (id) ON DELETE SET NULL
);

CREATE INDEX idx_shows_media_id ON shows (media_id);
CREATE INDEX idx_shows_network ON shows (network);
CREATE INDEX idx_shows_start_year ON shows (start_year);

CREATE TABLE show_collections (
  id   TEXT PRIMARY KEY DEFAULT nanoid(10),
  name CITEXT NOT NULL UNIQUE
);

CREATE TABLE show_episodes (
  id             TEXT PRIMARY KEY DEFAULT nanoid(10),
  show_id        TEXT NOT NULL,
  season_number  INTEGER NOT NULL CHECK (season_number >= 0),
  episode_number INTEGER NOT NULL CHECK (episode_number >= 0),
  episode_name   TEXT,
  UNIQUE (show_id, season_number, episode_number),
  FOREIGN KEY (show_id) REFERENCES shows (id) ON DELETE CASCADE
);

CREATE INDEX idx_show_episodes_show_id ON show_episodes (show_id);

CREATE TABLE actors (
  id        TEXT PRIMARY KEY DEFAULT nanoid(10),
  name      CITEXT NOT NULL UNIQUE,
  pseudonym TEXT
);

CREATE TABLE genres (
  id   TEXT PRIMARY KEY DEFAULT nanoid(10),
  name CITEXT NOT NULL UNIQUE
);

CREATE TABLE actor_movie_relationship (
  movie_id      TEXT NOT NULL,
  actor_id      TEXT NOT NULL,
  billing_order INTEGER NOT NULL CHECK (billing_order >= 1),
  PRIMARY KEY (movie_id, actor_id),
  FOREIGN KEY (movie_id) REFERENCES movies (id) ON DELETE CASCADE,
  FOREIGN KEY (actor_id) REFERENCES actors (id) ON DELETE RESTRICT
);

CREATE INDEX idx_am_actor ON actor_movie_relationship (actor_id);

CREATE TABLE actor_show_relationship (
  show_id       TEXT NOT NULL,
  actor_id      TEXT NOT NULL,
  billing_order INTEGER NOT NULL CHECK (billing_order >= 1),
  PRIMARY KEY (show_id, actor_id),
  FOREIGN KEY (show_id) REFERENCES shows (id) ON DELETE CASCADE,
  FOREIGN KEY (actor_id) REFERENCES actors (id) ON DELETE RESTRICT
);

CREATE INDEX idx_as_actor ON actor_show_relationship (actor_id);

CREATE TABLE movie_genre_relationship (
  movie_id TEXT NOT NULL,
  genre_id TEXT NOT NULL,
  PRIMARY KEY (movie_id, genre_id),
  FOREIGN KEY (movie_id) REFERENCES movies (id) ON DELETE CASCADE,
  FOREIGN KEY (genre_id) REFERENCES genres (id) ON DELETE RESTRICT
);

CREATE INDEX idx_mg_genre ON movie_genre_relationship (genre_id);

CREATE TABLE show_genre_relationship (
  show_id  TEXT NOT NULL,
  genre_id TEXT NOT NULL,
  PRIMARY KEY (show_id, genre_id),
  FOREIGN KEY (show_id) REFERENCES shows (id) ON DELETE CASCADE,
  FOREIGN KEY (genre_id) REFERENCES genres (id) ON DELETE RESTRICT
);

CREATE INDEX idx_sg_genre ON show_genre_relationship (genre_id);

CREATE TABLE movie_collection_relationship (
  movie_id      TEXT NOT NULL,
  collection_id TEXT NOT NULL,
  PRIMARY KEY (movie_id, collection_id),
  FOREIGN KEY (movie_id) REFERENCES movies (id) ON DELETE CASCADE,
  FOREIGN KEY (collection_id) REFERENCES movie_collections (id) ON DELETE RESTRICT
);

CREATE INDEX idx_mc_collection ON movie_collection_relationship (collection_id);

CREATE TABLE show_collection_relationship (
  show_id       TEXT NOT NULL,
  collection_id TEXT NOT NULL,
  PRIMARY KEY (show_id, collection_id),
  FOREIGN KEY (show_id) REFERENCES shows (id) ON DELETE CASCADE,
  FOREIGN KEY (collection_id) REFERENCES show_collections (id) ON DELETE RESTRICT
);

CREATE INDEX idx_sc_collection ON show_collection_relationship (collection_id);
