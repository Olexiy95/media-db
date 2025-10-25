from fastapi import Request, Form, status, APIRouter, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.db.db_control import MediaDB
from sqlite3 import IntegrityError
from app.models import ActorIn
from contextlib import asynccontextmanager
from app.deps import get_db, get_templates


router = APIRouter(prefix="/actors", tags=["actors"])


@router.get("")
def list_actors(
    request: Request,
    db: MediaDB = Depends(get_db),
    templates: Jinja2Templates = Depends(get_templates),
):
    """Returns a list of unique actors with the number of movies they appear in."""
    actors = db.get_actors()
    return templates.TemplateResponse(
        "actors.html", {"request": request, "actors": actors}
    )


@router.post("")
def create_actor(
    full_name: str = Form(...),
    pseudonym: str | None = Form(None),
    db: MediaDB = Depends(get_db),
    templates: Jinja2Templates = Depends(get_templates),
):
    data = ActorIn(full_name=full_name, pseudonym=pseudonym)
    try:
        db.insert_actor(data.full_name, data.pseudonym)
    except IntegrityError:  # sqlite3.IntegrityError or sqlalchemy.exc.IntegrityError
        return RedirectResponse(
            url="/actors?error=exists",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    return RedirectResponse(
        url="/actors?added=1",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/new")
def new_actor():
    return RedirectResponse(url="/actors", status_code=307)


@router.get("/{actor_id}")
def actor_detail(
    request: Request,
    actor_id: str,
    db: MediaDB = Depends(get_db),
    templates: Jinja2Templates = Depends(get_templates),
):
    actor = db.get_actor_by_id(actor_id)

    if actor is None:
        return templates.TemplateResponse(
            "404.html", {"request": request}, status_code=404
        )

    return templates.TemplateResponse(
        "actor_detail.html", {"request": request, "actor": actor}
    )
