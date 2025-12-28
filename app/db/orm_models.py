from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.associationproxy import association_proxy


class Base(DeclarativeBase):
    pass


# NOTE: app_meta has NO primary key in your SQL.
# ORM needs a PK to do normal identity / updates cleanly.
# If you truly want ORM ops on it, add a PK in SQL.
# Otherwise, leave it unmapped or map as a Core Table.
class AppMeta(Base):
    __tablename__ = "app_meta"

    # "best-effort" mapping: treat last_updated as a pseudo-PK.
    # Works if you only ever keep a single row and update it in-place.
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        primary_key=True,
    )
    last_backup: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class Director(Base):
    __tablename__ = "directors"

    id: Mapped[str] = mapped_column(
        Text, primary_key=True, server_default=text("nanoid(10)")
    )
    name: Mapped[str] = mapped_column(CITEXT, nullable=False, unique=True)

    movies: Mapped[List["Movie"]] = relationship(back_populates="director")


class Media(Base):
    __tablename__ = "media"

    id: Mapped[str] = mapped_column(
        Text, primary_key=True, server_default=text("nanoid(10)")
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[Optional[int]] = mapped_column(Integer)
    artwork_path: Mapped[Optional[str]] = mapped_column(Text)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    obtained: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    sort_title: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(Text, nullable=False)

    movie: Mapped[Optional["Movie"]] = relationship(
        back_populates="media", uselist=False
    )
    show: Mapped[Optional["Show"]] = relationship(back_populates="media", uselist=False)


class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[str] = mapped_column(
        Text, primary_key=True, server_default=text("nanoid(10)")
    )
    media_id: Mapped[str] = mapped_column(
        Text, ForeignKey("media.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    year: Mapped[Optional[int]] = mapped_column(Integer)
    director_id: Mapped[Optional[str]] = mapped_column(
        "director",
        Text,
        ForeignKey("directors.id", ondelete="SET NULL"),
    )
    duration: Mapped[Optional[int]] = mapped_column(Integer)

    media: Mapped["Media"] = relationship(back_populates="movie")
    director: Mapped[Optional["Director"]] = relationship(back_populates="movies")

    actor_links: Mapped[List["ActorMovie"]] = relationship(
        back_populates="movie",
        cascade="all, delete-orphan",
    )
    actors: Mapped[List["Actor"]] = association_proxy("actor_links", "actor")  # type: ignore

    genre_links: Mapped[List["MovieGenre"]] = relationship(
        back_populates="movie",
        cascade="all, delete-orphan",
    )
    genres: Mapped[List["Genre"]] = association_proxy("genre_links", "genre")  # type: ignore

    collection_links: Mapped[List["MovieCollectionLink"]] = relationship(
        back_populates="movie",
        cascade="all, delete-orphan",
    )
    collections: Mapped[List["MovieCollection"]] = association_proxy(
        "collection_links", "collection"
    )  # type: ignore


class MovieCollection(Base):
    __tablename__ = "movie_collections"

    id: Mapped[str] = mapped_column(
        Text, primary_key=True, server_default=text("nanoid(10)")
    )
    name: Mapped[str] = mapped_column(CITEXT, nullable=False, unique=True)

    movie_links: Mapped[List["MovieCollectionLink"]] = relationship(
        back_populates="collection",
        cascade="all, delete-orphan",
    )
    movies: Mapped[List["Movie"]] = association_proxy("movie_links", "movie")  # type: ignore


class ShowNetwork(Base):
    __tablename__ = "show_networks"

    id: Mapped[str] = mapped_column(
        Text, primary_key=True, server_default=text("nanoid(10)")
    )
    name: Mapped[str] = mapped_column(CITEXT, nullable=False, unique=True)

    shows: Mapped[List["Show"]] = relationship(back_populates="network")


class Show(Base):
    __tablename__ = "shows"

    id: Mapped[str] = mapped_column(
        Text, primary_key=True, server_default=text("nanoid(10)")
    )
    media_id: Mapped[str] = mapped_column(
        Text, ForeignKey("media.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    start_year: Mapped[Optional[int]] = mapped_column(Integer)
    end_year: Mapped[Optional[int]] = mapped_column(Integer)

    network_id: Mapped[Optional[str]] = mapped_column(
        "network",
        Text,
        ForeignKey("show_networks.id", ondelete="SET NULL"),
    )

    media: Mapped["Media"] = relationship(back_populates="show")
    network: Mapped[Optional["ShowNetwork"]] = relationship(back_populates="shows")

    episodes: Mapped[List["ShowEpisode"]] = relationship(
        back_populates="show",
        cascade="all, delete-orphan",
    )

    actor_links: Mapped[List["ActorShow"]] = relationship(
        back_populates="show",
        cascade="all, delete-orphan",
    )
    actors: Mapped[List["Actor"]] = association_proxy("actor_links", "actor")  # type: ignore

    genre_links: Mapped[List["ShowGenre"]] = relationship(
        back_populates="show",
        cascade="all, delete-orphan",
    )
    genres: Mapped[List["Genre"]] = association_proxy("genre_links", "genre")  # type: ignore

    collection_links: Mapped[List["ShowCollectionLink"]] = relationship(
        back_populates="show",
        cascade="all, delete-orphan",
    )
    collections: Mapped[List["ShowCollection"]] = association_proxy(
        "collection_links", "collection"
    )  # type: ignore


class ShowCollection(Base):
    __tablename__ = "show_collections"

    id: Mapped[str] = mapped_column(
        Text, primary_key=True, server_default=text("nanoid(10)")
    )
    name: Mapped[str] = mapped_column(CITEXT, nullable=False, unique=True)

    show_links: Mapped[List["ShowCollectionLink"]] = relationship(
        back_populates="collection",
        cascade="all, delete-orphan",
    )
    shows: Mapped[List["Show"]] = association_proxy("show_links", "show")  # type: ignore


class ShowEpisode(Base):
    __tablename__ = "show_episodes"

    id: Mapped[str] = mapped_column(
        Text, primary_key=True, server_default=text("nanoid(10)")
    )
    show_id: Mapped[str] = mapped_column(
        Text, ForeignKey("shows.id", ondelete="CASCADE"), nullable=False
    )

    season_number: Mapped[int] = mapped_column(Integer, nullable=False)
    episode_number: Mapped[int] = mapped_column(Integer, nullable=False)
    episode_name: Mapped[Optional[str]] = mapped_column(Text)

    show: Mapped["Show"] = relationship(back_populates="episodes")


class Actor(Base):
    __tablename__ = "actors"

    id: Mapped[str] = mapped_column(
        Text, primary_key=True, server_default=text("nanoid(10)")
    )
    name: Mapped[str] = mapped_column(CITEXT, nullable=False, unique=True)
    pseudonym: Mapped[Optional[str]] = mapped_column(Text)

    movie_links: Mapped[List["ActorMovie"]] = relationship(back_populates="actor")
    movies: Mapped[List["Movie"]] = association_proxy("movie_links", "movie")  # type: ignore

    show_links: Mapped[List["ActorShow"]] = relationship(back_populates="actor")
    shows: Mapped[List["Show"]] = association_proxy("show_links", "show")  # type: ignore


class Genre(Base):
    __tablename__ = "genres"

    id: Mapped[str] = mapped_column(
        Text, primary_key=True, server_default=text("nanoid(10)")
    )
    name: Mapped[str] = mapped_column(CITEXT, nullable=False, unique=True)

    movie_links: Mapped[List["MovieGenre"]] = relationship(back_populates="genre")
    movies: Mapped[List["Movie"]] = association_proxy("movie_links", "movie")  # type: ignore

    show_links: Mapped[List["ShowGenre"]] = relationship(back_populates="genre")
    shows: Mapped[List["Show"]] = association_proxy("show_links", "show")  # type: ignore


# ---- association objects ----
# (Using explicit classes because you have extra fields like billing_order,
# and because it makes operations cleaner than "secondary=" when you want metadata.)


class ActorMovie(Base):
    __tablename__ = "actor_movie_relationship"

    movie_id: Mapped[str] = mapped_column(
        Text, ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True
    )
    actor_id: Mapped[str] = mapped_column(
        Text, ForeignKey("actors.id", ondelete="RESTRICT"), primary_key=True
    )
    billing_order: Mapped[int] = mapped_column(Integer, nullable=False)

    movie: Mapped["Movie"] = relationship(back_populates="actor_links")
    actor: Mapped["Actor"] = relationship(back_populates="movie_links")


class ActorShow(Base):
    __tablename__ = "actor_show_relationship"

    show_id: Mapped[str] = mapped_column(
        Text, ForeignKey("shows.id", ondelete="CASCADE"), primary_key=True
    )
    actor_id: Mapped[str] = mapped_column(
        Text, ForeignKey("actors.id", ondelete="RESTRICT"), primary_key=True
    )
    billing_order: Mapped[int] = mapped_column(Integer, nullable=False)

    show: Mapped["Show"] = relationship(back_populates="actor_links")
    actor: Mapped["Actor"] = relationship(back_populates="show_links")


class MovieGenre(Base):
    __tablename__ = "movie_genre_relationship"

    movie_id: Mapped[str] = mapped_column(
        Text, ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True
    )
    genre_id: Mapped[str] = mapped_column(
        Text, ForeignKey("genres.id", ondelete="RESTRICT"), primary_key=True
    )

    movie: Mapped["Movie"] = relationship(back_populates="genre_links")
    genre: Mapped["Genre"] = relationship(back_populates="movie_links")


class ShowGenre(Base):
    __tablename__ = "show_genre_relationship"

    show_id: Mapped[str] = mapped_column(
        Text, ForeignKey("shows.id", ondelete="CASCADE"), primary_key=True
    )
    genre_id: Mapped[str] = mapped_column(
        Text, ForeignKey("genres.id", ondelete="RESTRICT"), primary_key=True
    )

    show: Mapped["Show"] = relationship(back_populates="genre_links")
    genre: Mapped["Genre"] = relationship(back_populates="show_links")


class MovieCollectionLink(Base):
    __tablename__ = "movie_collection_relationship"

    movie_id: Mapped[str] = mapped_column(
        Text, ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True
    )
    collection_id: Mapped[str] = mapped_column(
        Text, ForeignKey("movie_collections.id", ondelete="RESTRICT"), primary_key=True
    )

    movie: Mapped["Movie"] = relationship(back_populates="collection_links")
    collection: Mapped["MovieCollection"] = relationship(back_populates="movie_links")


class ShowCollectionLink(Base):
    __tablename__ = "show_collection_relationship"

    show_id: Mapped[str] = mapped_column(
        Text, ForeignKey("shows.id", ondelete="CASCADE"), primary_key=True
    )
    collection_id: Mapped[str] = mapped_column(
        Text, ForeignKey("show_collections.id", ondelete="RESTRICT"), primary_key=True
    )

    show: Mapped["Show"] = relationship(back_populates="collection_links")
    collection: Mapped["ShowCollection"] = relationship(back_populates="show_links")
