from pydantic import BaseModel


class MovieBase(BaseModel):
    title: str
    director: str
    year: int


class MovieCreate(MovieBase):
    pass


class MovieSchema(MovieBase):
    id: str  # Assuming the ID is a string of a shortened UUID

    class Config:
        orm_mode = True
