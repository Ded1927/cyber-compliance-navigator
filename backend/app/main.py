from fastapi import FastAPI

from app.api.anonymous import router as anonymous_router
from app.api.auth import router as auth_router
from app.api.export import router as export_router
from app.api.questionnaire import router as questionnaire_router
from app.core.database import init_db

app = FastAPI(title="CyberLaw Navigator UA API")

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
