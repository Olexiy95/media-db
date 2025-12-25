from fastapi import HTTPException, Request, APIRouter, Depends, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from app.db.db_control import MediaDB
from app.db.pydantic_models import MovieOut, MovieUpdate
from app.deps import get_db, get_templates

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("", response_class=HTMLResponse)
def list_movies(
    request: Request,
    db: MediaDB = Depends(get_db),
    templates: Jinja2Templates = Depends(get_templates),
):
    rows = db.get_movies()  # returns sqlite3.Row[]
    movies = [MovieOut(**dict(row)) for row in rows]
    return templates.TemplateResponse(
        "movies.html", {"request": request, "movies": movies}
    )


@router.get("/{movie_id}")
def movie_detail(
    request: Request,
    movie_id: str,
    db: MediaDB = Depends(get_db),
    templates: Jinja2Templates = Depends(get_templates),
):
    movie = db.get_movie_by_id(movie_id)

    if movie is None:
        return templates.TemplateResponse(
            "404.html", {"request": request}, status_code=404
        )

    return templates.TemplateResponse(
        "movie_detail.html", {"request": request, "movie": movie}
    )


@router.post("/{movie_id}/edit")
async def update_movie(
    movie_id: int, patch: MovieUpdate, db: MediaDB = Depends(get_db)
):
    """Updates a movie entry in the database."""
    changes = patch.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No fields provided")
    try:
        updated = db.update_movie(movie_id, changes)
    except KeyError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Movie not found")
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

    return {"success": True, "movie": updated}
