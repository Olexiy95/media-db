from fastapi import Form
from pydantic import BaseModel, field_validator
from typing import Optional, List, Union


class MovieOut(BaseModel):
    media_id: str
    movie_id: str
    title: str
    sort_title: str
    rating: Optional[float] = None
    year: Optional[int] = None
    genre: Optional[str] = None
    leading_actors: Optional[str] = None
    obtained: Optional[str] = None

    @field_validator("*", mode="before")
    def none_to_empty_strings(cls, v, info):
        if info.field_name in {"genre", "leading_actors", "obtained"} and v is None:
            return ""
        return v


class MovieUpdate(BaseModel):
    title: Optional[str] = None
    year: Optional[int] = None
    genre: Optional[str] = None
    leading_actors: Optional[str] = None
    rating: Optional[float] = None
    notes: Optional[str] = None
    obtained: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        title: str | None = Form(None),
        year: int | None = Form(None),
        genre: list[str] | None = Form(None),
        rating: float | None = Form(None),
        notes: str | None = Form(None),
        leading_actors: str | None = Form(None),
        obtained: str | None = Form(None),
    ) -> "MovieUpdate":
        return cls(
            title=title,
            year=year,
            genre="; ".join(genre) if genre else None,
            rating=rating,
            notes=notes,
            leading_actors=leading_actors,
            obtained=obtained,
        )


class ShowOut(BaseModel):
    media_id: str
    show_id: str
    title: str
    sort_title: str
    rating: Optional[float] = None
    year: Optional[int] = None
    genre: Optional[str] = None
    leading_actors: Optional[str] = None
    obtained: Optional[str] = None

    @field_validator("*", mode="before")
    def none_to_empty_strings(cls, v, info):
        if info.field_name in {"genre", "leading_actors", "obtained"} and v is None:
            return ""
        return v


class ActorIn(BaseModel):
    full_name: str
    pseudonym: Optional[str] = None


class ActorOut(BaseModel):
    id: str
    name: str
    pseudonym: Optional[str] = None
    movies: List[MovieOut] = []


class PageOut(BaseModel):
    items: Union[List[MovieOut], List[ShowOut]]
    limit: int
    offset: int
    total: int
