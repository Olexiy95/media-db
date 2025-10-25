from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.db.db_control import MediaDB
from contextlib import asynccontextmanager
from app.routers import api_router, movies_router, actors_router, shows_router


DB_DIR = "dbs"
DB_NAME = "scratch_test.db"


def check_db_exists():
    import os

    return os.path.exists(
        f"{DB_DIR}/{DB_NAME}",
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Checking if backup is needed...")
    yield


app = FastAPI(lifespan=lifespan)
app.state.mediaDB = MediaDB("dbs/scratch_test.db")
app.state.templates = Jinja2Templates(directory="app/static/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
# app.mount("/scripts", StaticFiles(directory="static/scripts"), name="scripts")
app.mount("/logos", StaticFiles(directory="resources/logos"), name="logos")

app.include_router(api_router)
app.include_router(movies_router, include_in_schema=False)
app.include_router(actors_router, include_in_schema=False)
app.include_router(shows_router, include_in_schema=False)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index(request: Request):
    counts = app.state.mediaDB.get_counts()
    return app.state.templates.TemplateResponse(
        "home.html", {"request": request, "counts": counts}
    )


@app.get("/collections", response_class=HTMLResponse, include_in_schema=False)
def list_collections(request: Request):
    # collections = mediaDB.get_collections()
    # return templates.TemplateResponse(
    #     "collections.html", {"request": request, "collections": collections}
    # )
    pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)
