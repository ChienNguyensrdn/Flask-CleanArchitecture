"""UTH Conference Management System - Main Application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi import jinja2response
from fastapi.responses import HTMLResponse

from app.core.config import get_settings
from app.core.database import init_db
from app.api import auth, conferences, papers, reviews, pc_members
from fastapi.templating import Jinja2Templates
from fastapi import Request

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("Starting UTH Conference Management System...")
    init_db()
    print("Database initialized!")
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    description="API for UTH Scientific Conference Paper Management System",
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React/Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(conferences.router, prefix="/api/v1")
app.include_router(papers.router, prefix="/api/v1")
app.include_router(reviews.router, prefix="/api/v1")
app.include_router(pc_members.router, prefix="/api/v1")


@app.get("/", response_class=HTMLResponse)
def home():
    return "<h1>Welcome to UTH Conference Management System API</h1>"
    templates = Jinja2Templates(directory="templates")

    @app.get("/login", response_class=HTMLResponse)
    def login(request: Request):
        return templates.TemplateResponse(request,"login.html", {"request": request})



@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "UTH-ConfMS API"}

