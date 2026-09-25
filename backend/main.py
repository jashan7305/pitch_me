from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from api.routes import router

from config import FRONTEND_DIR

app = FastAPI(title="PitchMe API")

app.include_router(router)

# Static frontend assets
app.mount(
    "/css",
    StaticFiles(directory=FRONTEND_DIR / "css"),
    name="css",
)

app.mount(
    "/js",
    StaticFiles(directory=FRONTEND_DIR / "js"),
    name="js",
)


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(FRONTEND_DIR / "html" / "index.html")


@app.get("/loading", include_in_schema=False)
def loading():
    return FileResponse(FRONTEND_DIR / "html" / "loading.html")


@app.get("/results", include_in_schema=False)
def results():
    return FileResponse(FRONTEND_DIR / "html" / "results.html")


@app.get("/health")
def health():
    return {"status": "ok"}
