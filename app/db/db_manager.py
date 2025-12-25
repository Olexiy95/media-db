import sqlite3
import pandas as pd
from nanoid import generate
from app.resource_loader import (
    get_genres as premade_genres_list,
    get_actors as premade_actors_list,
)
from app.utils import _norm_base, _parse_actor, _get_or_create_actor_id, _parse_years
import logging

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class MediaDBManager:
    """
    Manages the media database, including init and data import/seeding.
    """

    def __init__(
        self,
        movies_csv,
        shows_csv,
        db_path="media.db",
        sql_init_file="sql/init.sql",
    ):
        self.db_path = db_path
        self.movies_csv = movies_csv
        self.shows_csv = shows_csv
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        self.sql_init_file = sql_init_file
        self.alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

    # ====================== Database Initialisation ====================== #

    def initialise_tables(self):
        """Reads and executes SQL statements from a file to set up the database schema."""
        try:
            with open(self.sql_init_file, "r") as f:
                sql_script = f.read()

            self.cursor.executescript(sql_script)
            self.conn.commit()
            print(f"Database schema initialized from {self.sql_init_file}")
        except sqlite3.Error as e:
            print(f"Error executing SQL script: {e}")

    def initialise_views(self, views_sql_file="sql/views.sql"):
        """Reads and executes SQL statements from a file to set up the database views."""
        # Might move this to a Docker init later
        try:
            with open(views_sql_file, "r") as f:
                sql_script = f.read()

            self.cursor.executescript(sql_script)
            self.conn.commit()
            print(f"Database views initialized from {views_sql_file}")
        except sqlite3.Error as e:
            print(f"Error executing views SQL script: {e}")

    def initialise_database(self):
        """Initialises the database by creating tables and views."""
        self.initialise_tables()
        self.initialise_views()

    # ====================== Helpers ====================== #

    def generate_id(self, length: int = 10) -> str:
        return generate(self.alphabet, length)

    def normalize_sort_title(self, title: str) -> str:
        sort_title = title.strip().lower()
        for prefix in ("the ", "a ", "an "):
            if sort_title.startswith(prefix):
                return sort_title[len(prefix) :]
        return sort_title

    def get_normalised_df(self, csv_file: str) -> pd.DataFrame:
        df = pd.read_csv(csv_file)
        df.columns = df.columns.str.lower()
        return df

    def _get_or_create_actor_id(self, name: str) -> str:
        base, pseudo = _parse_actor(name)
        if not base:
            return ""  # caller should skip empty

        # lookup by BASE NAME only
        row = self.cursor.execute(
            "SELECT id, pseudonym FROM actors WHERE name = ? COLLATE NOCASE",
            (base,),
        ).fetchone()

        if row:
            actor_id, existing_pseudo = row[0], row[1]
            # upgrade pseudonym if we learned one
            if (existing_pseudo is None or existing_pseudo == "") and pseudo:
                self.cursor.execute(
                    "UPDATE actors SET pseudonym = ? WHERE id = ?",
                    (pseudo, actor_id),
                )
            return actor_id

        # insert new actor with base name + optional pseudonym
        new_id = self.generate_id()
        self.cursor.execute(
            "INSERT OR IGNORE INTO actors (id, name, pseudonym) VALUES (?, ?, ?)",
            (new_id, base, pseudo),
        )
        return new_id

    # ====================== Insertion Methods ====================== #
    def insert_genres(self, movie_csv_file: str | None = None) -> int:
        """Insert genres into the database if they don't exist.
        Sources:
        - premade_genres_list()
        - any CSV column whose header contains 'genre' (case-insensitive)
        Splits comma-separated cells, trims whitespace, dedupes case-insensitively.
        Returns: number of rows attempted to insert (INSERT OR IGNORE may drop dups).
        """

        def _clean(name: str) -> str:
            # strip & collapse internal whitespace
            return " ".join(name.strip().split())

        def _norm(name: str) -> str:
            # case-insensitive dedupe key
            return _clean(name).lower()

        seen: set[str] = set()
        genres: list[str] = []

        # 1) seed from premade list (if available)
        try:
            for g in premade_genres_list():
                if not g:
                    continue
                name = _clean(str(g))
                if name:  # allow short names like "SF", "TV"
                    key = _norm(name)
                    if key not in seen:
                        seen.add(key)
                        genres.append(name)
        except NameError:
            pass  # no premade list available; skip quietly

        # 2) add from CSV (if provided)
        if movie_csv_file is None:
            movie_csv_file = getattr(self, "movies_csv", None)

        if movie_csv_file:
            df = self.get_normalised_df(movie_csv_file)

            # find all columns containing 'genre' (case-insensitive)
            genre_cols = df.filter(regex=r"(?i)genre", axis=1).columns.tolist()

            for col in genre_cols:
                for cell in df[col].dropna():
                    # split by comma; ignore empties
                    for raw in str(cell).split(","):
                        name = _clean(raw)
                        if not name:
                            continue
                        key = _norm(name)
                        if key not in seen:
                            seen.add(key)
                            genres.append(name)

        # 3) bulk insert
        rows = [(self.generate_id(5), g) for g in genres]
        if rows:
            self.cursor.executemany(
                "INSERT OR IGNORE INTO genres (id, name) VALUES (?, ?)",
                rows,
            )
            self.conn.commit()

        return len(rows)

    def insert_actors(self, csv_file: str | None = None) -> int:
        """
        Insert actors once per canonical base name.
        Prefer the variant that carries a pseudonym if both appear.
        """
        # base_key -> {"name": base_name, "pseudonym": str|None}
        merged: dict[str, dict] = {}

        # 1) seed from premade list
        try:
            for a in premade_actors_list():
                base, pseudo = _parse_actor(a)
                if not base:
                    continue
                key = _norm_base(base)
                cur = merged.get(key)
                if cur is None:
                    merged[key] = {"name": base, "pseudonym": pseudo}
                else:
                    # upgrade to keep pseudonym if we didn’t have one
                    if cur.get("pseudonym") in (None, "") and pseudo:
                        cur["pseudonym"] = pseudo
        except NameError:
            pass

        # 2) pull from CSV
        if csv_file is None:
            csv_file = getattr(self, "movies_csv", None)

        if csv_file:
            df = self.get_normalised_df(csv_file)
            actor_cols = df.filter(regex=r"(?i)actor", axis=1).columns.tolist()

            for col in actor_cols:
                for cell in df[col].dropna():
                    for piece in str(cell).split(","):
                        base, pseudo = _parse_actor(piece)
                        if not base:
                            continue
                        key = _norm_base(base)
                        cur = merged.get(key)
                        if cur is None:
                            merged[key] = {"name": base, "pseudonym": pseudo}
                        else:
                            if cur.get("pseudonym") in (None, "") and pseudo:
                                cur["pseudonym"] = pseudo

        # 3) bulk insert
        actors = list(merged.values())
        rows = [(self.generate_id(), a["name"], a["pseudonym"]) for a in actors]
        if rows:
            self.cursor.executemany(
                """
                    INSERT INTO actors (id, name, pseudonym)
                    VALUES (?, ?, ?)
                    ON CONFLICT(name) DO UPDATE SET
                        pseudonym = COALESCE(excluded.pseudonym, actors.pseudonym)
                    """,
                rows,  # or single execute for _get_or_create
            )
            self.conn.commit()

        return len(rows)

    def insert_movies(self) -> int:
        """Insert movies and link genres/actors from the CSV into DB."""
        df = pd.read_csv(self.movies_csv)
        df.columns = df.columns.str.strip().str.lower()

        # Drop rows with no title
        df = df.dropna(subset=["title"])  # drop actual NaN
        df["title"] = df["title"].str.strip()  # strip whitespace
        df = df[df["title"] != ""]

        # Normalized fields
        df["sort_title"] = df["title"].apply(self.normalize_sort_title)
        df["year"] = pd.to_numeric(df.get("year"), errors="coerce").astype("Int64")  # type: ignore

        def _bool_to01(s: pd.Series) -> pd.Series:
            return (
                s.astype(str)
                .str.strip()
                .str.lower()
                .map(
                    {
                        "yes": 1,
                        "true": 1,
                        "1": 1,
                        "y": 1,
                        "no": 0,
                        "false": 0,
                        "0": 0,
                        "n": 0,
                        "": 0,
                        "nan": 0,
                    }
                )
                .fillna(0)
                .astype("Int64")
            )

        if "obtained" in df.columns:
            df["obtained"] = _bool_to01(df["obtained"])
        else:
            df["obtained"] = 0

        df["rating"] = (
            pd.to_numeric(df.get("rating"), errors="coerce").fillna(0).astype(int)  # type: ignore
        )
        df["notes"] = df.get("notes", "").fillna("").astype(str)  # type: ignore
        df["artwork_path"] = (
            df["artwork_path"].fillna("").astype(str)
            if "artwork_path" in df.columns
            else pd.Series([""] * len(df), dtype=str)
        )  # type: ignore

        # Helpers
        def _clean(s: str) -> str:
            return " ".join(str(s).strip().split())

        def _split_list(cell) -> list[str]:
            if pd.isna(cell) or not cell:
                return []
            return [_clean(x) for x in str(cell).split(",") if _clean(x)]

        def _get_or_create_genre_id(name: str) -> str:
            row = self.cursor.execute(
                "SELECT id FROM genres WHERE name = ? COLLATE NOCASE", (name,)
            ).fetchone()
            if row:
                return row[0]
            new_id = self.generate_id(5)
            self.cursor.execute(
                "INSERT OR IGNORE INTO genres (id, name) VALUES (?, ?)",
                (new_id, name),
            )
            return new_id

        actor_cols = df.filter(regex=r"(?i)actor", axis=1).columns.tolist()
        genre_cols = df.filter(regex=r"(?i)genre", axis=1).columns.tolist()

        movies_inserted = 0

        for _, row in df.iterrows():
            media_id = self.generate_id()
            movie_id = self.generate_id()

            self.cursor.execute(
                """
                INSERT INTO media
                (id, title, rating, artwork_path, notes, obtained, sort_title, type)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'movie')
                """,
                (
                    media_id,
                    row["title"],
                    int(row["rating"]),
                    row["artwork_path"],
                    row["notes"],
                    int(row["obtained"]) if pd.notna(row["obtained"]) else 0,
                    row["sort_title"],
                ),
            )

            self.cursor.execute(
                "INSERT INTO movies (id, media_id, year, duration) VALUES (?, ?, ?, ?)",
                (
                    movie_id,
                    media_id,
                    None if pd.isna(row["year"]) else int(row["year"]),
                    (
                        None
                        if "duration" not in row or pd.isna(row["duration"])
                        else int(row["duration"])
                    ),
                ),
            )

            # Link actors
            if actor_cols:
                actors = []
            # Link actors (ordered)
            if actor_cols:
                actors: list[str] = []
                for col in actor_cols:
                    actors.extend(_split_list(row[col]))  # left-to-right

                seen: set[str] = set()
                billing = 1
                for raw_actor in actors:
                    base, _ = _parse_actor(raw_actor)
                    if not base or len(base) < 3:
                        continue
                    k = base.lower()
                    if k in seen:
                        continue
                    seen.add(k)

                    actor_id = _get_or_create_actor_id(
                        self, raw_actor
                    )  # uses base internally
                    if actor_id:
                        self.cursor.execute(
                            "INSERT OR IGNORE INTO actor_movie_relationship (movie_id, actor_id, billing_order) VALUES (?, ?, ?)",
                            (movie_id, actor_id, billing),
                        )
                        billing += 1

            # Link genres
            if genre_cols:
                genres = []
                for col in genre_cols:
                    genres.extend(_split_list(row[col]))
                seen = set()
                for g in genres:
                    k = g.lower()
                    if k not in seen:
                        seen.add(k)
                        genre_id = _get_or_create_genre_id(g)
                        self.cursor.execute(
                            "INSERT OR IGNORE INTO movie_genre_relationship (movie_id, genre_id) VALUES (?, ?)",
                            (movie_id, genre_id),
                        )

            movies_inserted += 1

        self.conn.commit()
        return movies_inserted

    def insert_shows(self) -> int:
        """Insert shows and link genres/actors/networks from the CSV into DB."""

        df = pd.read_csv(self.shows_csv)
        df.columns = df.columns.str.strip().str.lower()

        # Drop rows with no title
        df = df.dropna(subset=["title"])
        df["title"] = df["title"].str.strip()
        df = df[df["title"] != ""]

        # Normalized / coerced fields
        df["sort_title"] = df["title"].apply(self.normalize_sort_title)

        def _bool_to01(s: pd.Series) -> pd.Series:
            return (
                s.astype(str)
                .str.strip()
                .str.lower()
                .map(
                    {
                        "yes": 1,
                        "true": 1,
                        "1": 1,
                        "y": 1,
                        "no": 0,
                        "false": 0,
                        "0": 0,
                        "n": 0,
                        "": 0,
                        "nan": 0,
                    }
                )
                .fillna(0)
                .astype("Int64")
            )

        if "obtained" in df.columns:
            df["obtained"] = _bool_to01(df["obtained"])
        else:
            df["obtained"] = 0

        df["rating"] = pd.to_numeric(df.get("rating"), errors="coerce").fillna(0).astype(int)  # type: ignore
        df["notes"] = df.get("notes", "").fillna("").astype(str)  # type: ignore
        df["artwork_path"] = (
            df["artwork_path"].fillna("").astype(str)
            if "artwork_path" in df.columns
            else pd.Series([""] * len(df), dtype=str)
        )  # type: ignore

        # Helpers
        def _clean(s: str) -> str:
            return " ".join(str(s).strip().split())

        def _split_list(cell) -> list[str]:
            if pd.isna(cell) or not cell:
                return []
            return [_clean(x) for x in str(cell).split(",") if _clean(x)]

        def _get_or_create_genre_id(name: str) -> str:
            row = self.cursor.execute(
                "SELECT id FROM genres WHERE name = ? COLLATE NOCASE", (name,)
            ).fetchone()
            if row:
                return row[0]
            new_id = self.generate_id(5)
            self.cursor.execute(
                "INSERT OR IGNORE INTO genres (id, name) VALUES (?, ?)",
                (new_id, name),
            )
            return new_id

        def _get_or_create_network_id(name: str) -> str | None:
            if not name:
                return None
            # Prefer a table `show_networks(id, name)`; create if not present
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS show_networks (id TEXT PRIMARY KEY, name TEXT UNIQUE)"
            )
            row = self.cursor.execute(
                "SELECT id FROM show_networks WHERE name = ? COLLATE NOCASE", (name,)
            ).fetchone()
            if row:
                return row[0]
            new_id = self.generate_id(5)
            self.cursor.execute(
                "INSERT OR IGNORE INTO show_networks (id, name) VALUES (?, ?)",
                (new_id, name),
            )
            return new_id

        # Detect optional relationship tables (be defensive)
        existing_tables = {
            r[0]
            for r in self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        have_actor_rel = "actor_show_relationship" in existing_tables
        have_genre_rel = "show_genre_relationship" in existing_tables

        actor_cols = df.filter(regex=r"(?i)actor", axis=1).columns.tolist()
        genre_cols = df.filter(regex=r"(?i)genre", axis=1).columns.tolist()

        shows_inserted = 0

        for _, row in df.iterrows():
            media_id = self.generate_id()
            show_id = self.generate_id()

            # Network: allow either an id or a name in CSV.
            network_id: str | None = None
            if "network" in df.columns:
                # If user passed a comma list, take first non-empty
                networks = _split_list(row["network"])
                network_name = networks[0] if networks else _clean(str(row["network"]))
                # If it's already an id present in show_networks, keep it; otherwise create by name
                if network_name:
                    # Try as id first
                    hit = self.cursor.execute(
                        "SELECT id FROM show_networks WHERE id = ?", (network_name,)
                    ).fetchone()
                    if hit:
                        network_id = hit[0]
                    else:
                        network_id = _get_or_create_network_id(network_name)

            # Insert media
            self.cursor.execute(
                """
                INSERT INTO media
                (id, title, rating, artwork_path, notes, obtained, sort_title, type)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'show')
                """,
                (
                    media_id,
                    row["title"],
                    int(row["rating"]),
                    row["artwork_path"],
                    row["notes"],
                    int(row["obtained"]) if pd.notna(row["obtained"]) else 0,
                    row["sort_title"],
                ),
            )

            # Insert show
            start_year, end_year = _parse_years(
                row.get("year") or row.get("years") or ""
            )
            self.cursor.execute(
                "INSERT INTO shows (id, media_id, start_year, end_year, network) VALUES (?, ?, ?, ?, ?)",
                (show_id, media_id, start_year, end_year, network_id),
            )

            # Link actors (ordered) if table exists
            if have_actor_rel and actor_cols:
                actors: list[str] = []
                for col in actor_cols:
                    actors.extend(
                        _split_list(row[col])
                    )  # left-to-right for billing order

                seen: set[str] = set()
                billing = 1
                for raw_actor in actors:
                    base, _ = _parse_actor(raw_actor)
                    if not base or len(base) < 3:
                        continue
                    k = base.lower()
                    if k in seen:
                        continue
                    seen.add(k)

                    actor_id = _get_or_create_actor_id(
                        self, raw_actor
                    )  # uses base internally
                    if actor_id:
                        self.cursor.execute(
                            """
                            INSERT OR IGNORE INTO actor_show_relationship
                            (show_id, actor_id, billing_order)
                            VALUES (?, ?, ?)
                            """,
                            (show_id, actor_id, billing),
                        )
                        billing += 1

            # Link genres if table exists
            if have_genre_rel and genre_cols:
                genres: list[str] = []
                for col in genre_cols:
                    genres.extend(_split_list(row[col]))
                seen_g: set[str] = set()
                for g in genres:
                    k = g.lower()
                    if k in seen_g:
                        continue
                    seen_g.add(k)
                    genre_id = _get_or_create_genre_id(g)
                    self.cursor.execute(
                        """
                        INSERT OR IGNORE INTO show_genre_relationship
                        (show_id, genre_id) VALUES (?, ?)
                        """,
                        (show_id, genre_id),
                    )

            shows_inserted += 1

        self.conn.commit()
        return shows_inserted

    def full_run(self):
        """Runs the full init process in order."""
        log.info("Starting full database initialization and data import...")
        self.initialise_database()
        log.info("Inserting genres...")
        self.insert_genres()
        log.info("Inserting actors...")
        self.insert_actors()
        log.info("Inserting movies...")
        self.insert_movies()
        log.info("Inserting shows...")
        self.insert_shows()
        log.info("Data import complete.")

    def close(self):
        """Close the database connection."""
        self.conn.close()
