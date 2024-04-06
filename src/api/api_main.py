from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
import uuid
from db_models import SessionLocal, engine, Base, Movie
from schemas import MovieCreate, MovieSchema

app = FastAPI()
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def generate_short_uuid():
    return str(uuid.uuid4())[:8]


router = APIRouter()


@router.post("/movies/", response_model=MovieSchema)
def create_movie(movie: MovieCreate, db: Session = Depends(get_db)):
    db_movie = Movie(id=generate_short_uuid(), **movie.dict())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie


app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
