from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.content.catalog import load_catalog

APP_ROOT = Path(__file__).resolve().parent

app = FastAPI(
    title="GoodToGo",
    version="0.1.0",
    description="Self-hosted GoodToGo and continuity organizer",
)
app.mount("/static", StaticFiles(directory=APP_ROOT / "static"), name="static")
templates = Jinja2Templates(directory=APP_ROOT / "templates")


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; "
        "img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'"
    )
    return response


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    catalog = load_catalog()
    question_count = sum(len(section.questions) for section in catalog.workbook.sections)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "catalog": catalog,
            "question_count": question_count,
            "page_title": "GoodToGo",
        },
    )


@app.get("/private", response_class=HTMLResponse)
async def private_workbook(request: Request):
    catalog = load_catalog()
    return templates.TemplateResponse(
        request=request,
        name="private_workbook.html",
        context={"catalog": catalog, "page_title": "Private workbook"},
    )


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="settings.html",
        context={
            "page_title": "Appearance settings",
            "theme_modes": ["system", "light", "dark"],
            "color_schemes": ["ocean", "forest", "ember", "plum", "slate"],
        },
    )


@app.get("/api/v1/catalog")
async def get_catalog():
    return load_catalog().model_dump(mode="json")


@app.get("/health")
async def health():
    return {"status": "ok"}

