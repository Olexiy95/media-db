import sqlite3
from nanoid import generate


class MediaDB:
    """
    Handles CRUD operations for media records.
    """

    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        self.alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        self.cursor.execute("PRAGMA foreign_keys = ON;")

    def generate_id(self, length: int = 10) -> str:
        return generate(self.alphabet, length)

    def get_counts(self):
        with sqlite3.connect(self.db_file) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            movies_count = c.execute("SELECT COUNT(*) AS n FROM movies;").fetchone()[
                "n"
            ]
            actors_count = c.execute("SELECT COUNT(*) AS n FROM actors;").fetchone()[
                "n"
            ]

            try:
                shows_count = c.execute("SELECT COUNT(*) AS n FROM shows;").fetchone()[
                    "n"
                ]
                if shows_count == 0:
                    shows_count = 25
            except sqlite3.OperationalError:
                shows_count = 25

            try:
                media_total = c.execute("SELECT COUNT(*) AS n FROM media;").fetchone()[
                    "n"
                ]
            except sqlite3.OperationalError:
                media_total = None

            try:
                not_obtained = c.execute(
                    "SELECT COUNT(*) AS n FROM media WHERE COALESCE(obtained,0)=0;"
                ).fetchone()["n"]
            except sqlite3.OperationalError:
                not_obtained = None

        return {
            "movies": movies_count,
            "shows": shows_count,
            "actors": actors_count,
            "media_total": sum([movies_count, shows_count]),  # may be None
            "not_obtained": not_obtained,  # may be None
        }

    def get_movies(self):
        """Retrieve all movies with a new connection."""
        with sqlite3.connect(self.db_file) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM v_movie_table ORDER BY
                    sort_title COLLATE NOCASE ASC,
                    (year IS NULL) ASC,   -- puts NULLs last
                    year ASC;"""
            )
            return cursor.fetchall()

    def get_movie_by_id(self, movie_id):
        """Retrieve a movie by its ID."""
        with sqlite3.connect(self.db_file) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            row = cursor.execute(
                "SELECT * FROM v_movie_table WHERE movie_id = ?;", (movie_id,)
            ).fetchone()
            actors = cursor.execute(
                """
            SELECT a.id, a.name AS full_name
            FROM actor_movie_relationship am
            JOIN actors a ON a.id = am.actor_id
            WHERE am.movie_id = ?
            ORDER BY a.name COLLATE NOCASE;
            """,
                (movie_id,),
            ).fetchall()

            movie = dict(row)
            movie["actors"] = [dict(a) for a in actors]
            return movie

    def get_actors(self):
        """Retrieve all actors."""
        with sqlite3.connect(self.db_file) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """SELECT
                    a.actor_id,
                    a.name,
                    a.pseudonym,
                    COUNT(DISTINCT CASE WHEN a.type = 'movie' THEN a.movie_id END) AS movie_count,
                    COUNT(DISTINCT CASE WHEN a.type = 'show'  THEN a.show_id  END) AS show_count
                    FROM v_actor_page a
                    GROUP BY a.actor_id, a.name, a.pseudonym;
            """
            )
            return cursor.fetchall()

    def get_actor_by_id(self, actor_id: str):
        """Retrieve an actor and their movies/shows by actor ID."""
        with sqlite3.connect(self.db_file) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Actor info
            actor_row = cursor.execute(
                "SELECT id AS actor_id, name AS full_name, pseudonym FROM actors WHERE id = ?;",
                (actor_id,),
            ).fetchone()
            if not actor_row:
                return None

            # Movies
            movies = cursor.execute(
                """
                SELECT DISTINCT movie_id AS id, title, year
                FROM v_actor_page
                WHERE actor_id = ? AND type = 'movie' AND movie_id IS NOT NULL
                ORDER BY year ASC, sort_title;
                """,
                (actor_id,),
            ).fetchall()

            # Shows
            shows = cursor.execute(
                """
                SELECT DISTINCT show_id AS id, title, start_year, end_year
                FROM v_actor_page
                WHERE actor_id = ? AND type = 'show' AND show_id IS NOT NULL
                ORDER BY sort_title;
                """,
                (actor_id,),
            ).fetchall()

        # Build dict for the template
        return {
            "actor_id": actor_row["actor_id"],
            "full_name": actor_row["full_name"],
            "pseudonym": actor_row["pseudonym"],
            "movies": [dict(m) for m in movies],
            "shows": [dict(s) for s in shows],
        }

    def insert_actor(self, full_name: str, pseudonym: str | None = None):
        with sqlite3.connect(self.db_file) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO actors(id, name, pseudonym) VALUES (?, ?, ?)",
                (self.generate_id(), full_name, pseudonym),
            )
            conn.commit()
            return cur.lastrowid

    def get_collections(self):
        """Retrieve all collections."""
        with sqlite3.connect(self.db_file) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""SELECT * FROM v_collections;""")
            return cursor.fetchall()

    def insert_movie(self, data):
        """Insert a new movie into the database."""
        pass

    def update_movie(self, movie_id, data):
        """Update movie details by ID."""
        with sqlite3.connect(self.db_file) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE movies
                SET title = ?, year = ?, duration = ?, rating = ?
                WHERE id = ?;
                """,
                (
                    data.get("title"),
                    data.get("year"),
                    data.get("duration"),
                    data.get("rating"),
                    movie_id,
                ),
            )
            conn.commit()

    def delete_movie(self, movie_id):
        """Delete a movie by ID."""
        pass

    def get_shows(self):
        """Retrieve all shows."""
        with sqlite3.connect(self.db_file) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""SELECT * FROM v_show_table;""")
            return cursor.fetchall()

    def insert_show(self, title, start_year, end_year, network, rating):
        """Insert a new show into the database."""
        pass

    def update_show(
        self,
        show_id,
        title=None,
        start_year=None,
        end_year=None,
        network=None,
        rating=None,
    ):
        """Update show details by ID."""
        pass

    def delete_show(self, show_id):
        """Delete a show by ID."""
        pass

    def get_media_by_type(self, media_type):
        """Retrieve media by type (movie, show, etc.)."""
        pass

    def close(self):
        """Close the database connection."""
        self.conn.close()
