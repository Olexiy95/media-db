from fastapi import APIRouter
from app.db.pydantic_models import MovieOut, PageOut, ShowOut
from fastapi import Request, Depends
from app.db.db_control import MediaDB
from app.deps import get_db

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/movies_data", response_model=PageOut)
def read_movies_data(request: Request, db: MediaDB = Depends(get_db)):
    rows = db.get_movies()
    movies = [dict(row) for row in rows]
    movies_out = [MovieOut(**m) for m in movies]
    return PageOut(
        items=movies_out, limit=len(movies_out), offset=0, total=len(movies_out)
    )


@router.get("/shows_data", response_model=PageOut)
def read_shows_data(request: Request, db: MediaDB = Depends(get_db)):
    rows = db.get_shows()
    shows = [dict(row) for row in rows]
    shows_out = [ShowOut(**s) for s in shows]
    return PageOut(
        items=shows_out, limit=len(shows_out), offset=0, total=len(shows_out)
    )
