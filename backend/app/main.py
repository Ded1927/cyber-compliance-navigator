import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.anonymous import router as anonymous_router
from app.api.auth import router as auth_router
from app.api.export import router as export_router
from app.api.questionnaire import router as questionnaire_router
from app.core.database import init_db

app = FastAPI(title="CyberLaw Navigator UA API")

cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]

if cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(anonymous_router)
app.include_router(auth_router)
app.include_router(export_router)
app.include_router(questionnaire_router)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
