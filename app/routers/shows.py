from fastapi import Request, APIRouter, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from app.db.db_control import MediaDB
from app.deps import get_db, get_templates


router = APIRouter(prefix="/shows", tags=["shows"])


@router.get("", response_class=HTMLResponse, include_in_schema=False)
def list_shows(
    request: Request,
    db: MediaDB = Depends(get_db),
    templates: Jinja2Templates = Depends(get_templates),
):
    rows = db.get_shows()
    # shows = [dict(row) for row in rows]
    return templates.TemplateResponse("shows.html", {"request": request, "shows": rows})
