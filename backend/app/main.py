import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from .core.config import settings
from .core.database import engine, Base
from .core.seeder import seed_database
from .api import api_router
from .simulator import simulator_instance

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize DB tables
    Base.metadata.create_all(bind=engine)
    
    # 2. Seed initial operational data
    seed_database()
    
    # 3. Start telemetry simulator task if enabled
    sim_task = None
    if settings.SIMULATOR_ENABLED:
        sim_task = asyncio.create_task(simulator_instance.run())
        
    yield
    
    # Teardown
    if sim_task:
        simulator_instance.stop()
        try:
            await asyncio.wait_for(sim_task, timeout=2.0)
        except (asyncio.TimeoutError, asyncio.CancelledError):
            pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Railway Infrastructure Defense & Cyber-NOC Operations Platform",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Modular API Routers
app.include_router(api_router)

# Mount Static Assets
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/health")
def health_check():
    return {
        "status": "HEALTHY",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": "CONNECTED",
        "simulator_active": simulator_instance.is_running
    }

@app.get("/")
def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"message": "Railway Rakshak Cyber-NOC API v2.0 Operational"})
