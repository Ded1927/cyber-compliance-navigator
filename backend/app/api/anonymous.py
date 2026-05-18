"""Anonymous (unauthenticated) roadmap preview.

The endpoint lets visitors generate a roadmap without registering.
Nothing is persisted — the response is built from matching template
steps and returned as a plain list.
"""

from urllib.parse import quote

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.document_generation.roadmap_pdf import PDF_MIME_TYPE, RoadmapPdfGenerator
from app.schemas.questionnaire import QuestionnaireAnswers
from app.services.roadmap import RoadmapGeneratorService

router = APIRouter(prefix="/api/questionnaire", tags=["questionnaire"])


class AnonymousRoadmapTaskResponse:
    """Lightweight pydantic-free dict builder for anonymous results."""

    @staticmethod
    def from_template(template, index: int) -> dict:
        return {
            "index": index,
            "title": template.title,
            "description": template.description,
            "guidance": template.instructions_text,
            "references": template.references_text,
            "legal_basis": (
                template.legal_act.title if template.legal_act else "Внутрішня вимога"
            ),
            "deadline_days": template.deadline_days,
        }


@router.post("/anonymous-submit")
async def anonymous_submit(
    answers: QuestionnaireAnswers,
    db: AsyncSession = Depends(get_async_db),
) -> list[dict]:
    """Generate a roadmap preview without authentication.

    Returns matched template steps as plain dicts — nothing is saved
    to the database.
    """
    service = RoadmapGeneratorService()
    templates = await service.find_matching_templates(db=db, answers=answers)

    return [
        AnonymousRoadmapTaskResponse.from_template(template, index)
        for index, template in enumerate(templates, start=1)
    ]


class AnonymousRoadmapPdfTask(BaseModel):
    index: int
    title: str
    description: str
    guidance: str | None = None
    references: str | None = None
    legal_basis: str
    deadline_days: int


class AnonymousRoadmapPdfRequest(BaseModel):
    org_type_label: str
    tasks: list[AnonymousRoadmapPdfTask]


@router.post("/anonymous-export-pdf")
async def anonymous_export_pdf(
    payload: AnonymousRoadmapPdfRequest,
) -> StreamingResponse:
    """Export the anonymous roadmap preview to PDF."""
    generator = RoadmapPdfGenerator()
    tasks_dicts = [task.model_dump() for task in payload.tasks]
    pdf_stream = generator.generate(tasks=tasks_dicts, org_type_label=payload.org_type_label)

    filename = "roadmap.pdf"
    quoted = quote(filename)

    return StreamingResponse(
        pdf_stream,
        media_type=PDF_MIME_TYPE,
        headers={
            "Content-Disposition": f"attachment; filename={filename}; filename*=UTF-8''{quoted}",
        },
    )
