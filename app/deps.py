from fastapi import Request, Depends
from fastapi.templating import Jinja2Templates
from app.db.db_control import MediaDB


def get_db(request: Request) -> MediaDB:
    return request.app.state.mediaDB


def get_templates(request: Request) -> Jinja2Templates:
    return request.app.state.templates
