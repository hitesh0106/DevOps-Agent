"""
DevOps Agent — FastAPI Application
=====================================
Main entry point for the API server. Serves the dashboard and API endpoints.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from config.settings import settings
from config.logging_config import setup_logging, get_logger
from api.routes.agent_routes import router as agent_router
from api.routes.pipeline_routes import router as pipeline_router
from api.routes.webhook_routes import router as webhook_router
from api.routes.monitoring_routes import router as monitoring_router
from api.routes.auth_routes import router as auth_router

logger = get_logger(__name__)

# Initialize logging
setup_logging(log_level=settings.log_level)

# Create FastAPI app
app = FastAPI(
    title="DevOps Agent API",
    description="AI-Powered Infrastructure Automation Agent",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount dashboard static files
dashboard_dir = Path(__file__).resolve().parent.parent / "dashboard"
if dashboard_dir.exists():
    app.mount("/css", StaticFiles(directory=str(dashboard_dir / "css")), name="css")
    app.mount("/js", StaticFiles(directory=str(dashboard_dir / "js")), name="js")
    if (dashboard_dir / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(dashboard_dir / "assets")), name="assets")

# Register API routes
app.include_router(agent_router, prefix="/api/agent", tags=["Agent"])
app.include_router(pipeline_router, prefix="/api/pipelines", tags=["Pipelines"])
app.include_router(webhook_router, prefix="/webhook", tags=["Webhooks"])
app.include_router(monitoring_router, prefix="/api/monitoring", tags=["Monitoring"])
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])


@app.get("/", include_in_schema=False)
async def serve_dashboard():
    """Serve the premium dashboard."""
    index_path = dashboard_dir / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "DevOps Agent API is running", "docs": "/docs"}


@app.get("/health")
async def health_check():
    """API health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "simulation_mode": settings.simulation_mode,
    }


@app.on_event("startup")
async def startup_event():
    logger.info("DevOps Agent API starting", port=settings.api_port, simulation=settings.simulation_mode)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("DevOps Agent API shutting down")
