from sqlalchemy import Column, String, Integer, create_engine, Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from common.utils import create_connection_string, get_db_connection

db_connection_string = create_connection_string(default_config=True)

engine: Engine = get_db_connection(db_connection_string)
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

Base = declarative_base()


class Movie(Base):
    __tablename__ = "movies"
    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    year = Column(Integer)
    genre = Column(String)
    leading_actors = Column(String)
    rating = Column(Integer)
    comments = Column(String)
    director = Column(String)


class Show(Base):
    __tablename__ = "shows"
    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    year = Column(Integer)
    seasons_episodes = Column(String)
    network = Column(String)
    genre = Column(String)
    leading_actors = Column(String)
    rating = Column(Integer)
    comments = Column(String)


class MusicAlbum(Base):
    __tablename__ = "albums"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    artist = Column(String)
    year = Column(Integer)


class MusicPodcast(Base):
    __tablename__ = "podcasts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    host = Column(String)
    duration_minutes = Column(Integer)


# View or join for all music types
class Music(Base):
    __table__ = None


# class Music(Base):
#     __tablename__ = "music"
#     id = Column(String, primary_key=True, index=True)
#     item_type_id = Column(Integer, ForeignKey("music_types.id"))
#     item_type = relationship("MusicType", back_populates="music")
#     title = Column(String, index=True)
#     artist = Column(String)
#     year = Column(Integer)
