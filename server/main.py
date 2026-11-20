from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from pathlib import Path

from scripts.seed_incidents import DATA_PATH

from src.config.chroma import add_incidents
from src.config.db import initialize_database
from src.config.env import settings
from src.routes.health import router as health_router
from src.routes.investigate import router as investigate_router
from src.routes.history import router as history_router
from src.routes.feedback import router as feedback_router


app = FastAPI(title="IncidentSense API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.allowed_origin],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(investigate_router, prefix="/api")
app.include_router(history_router, prefix="/api")
app.include_router(feedback_router, prefix="/api")


@app.on_event("startup")
def initialize_resources() -> None:
    initialize_database()
    incidents = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    add_incidents(incidents)
