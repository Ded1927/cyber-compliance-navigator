from urllib.parse import quote

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.document_generation.generator import (
    DOCX_MIME_TYPE,
    XLSX_MIME_TYPE,
    DocumentGenerator,
)
from app.models.system_register_item import SystemRegisterItem
from app.models.user import User
from app.schemas.export import CisoOrderContext
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/export", tags=["export"])


@router.post("/ciso-order.docx")
def export_ciso_order_docx(
    payload: CisoOrderContext,
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    generator = DocumentGenerator()
    file_stream = generator.generate_ciso_order_docx(payload.to_template_context())
    filename = _content_disposition_filename("ciso-order.docx")

    return StreamingResponse(
        file_stream,
        media_type=DOCX_MIME_TYPE,
        headers={"Content-Disposition": filename},
    )


@router.get("/system-register.xlsx")
def export_system_register_xlsx(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    systems = list(
        db.scalars(
            select(SystemRegisterItem)
            .where(SystemRegisterItem.user_id == current_user.id)
            .order_by(SystemRegisterItem.system_name)
        )
    )

    generator = DocumentGenerator()
    file_stream = generator.generate_system_register_xlsx(systems)
    filename = _content_disposition_filename("system-register.xlsx")

    return StreamingResponse(
        file_stream,
        media_type=XLSX_MIME_TYPE,
        headers={"Content-Disposition": filename},
    )


def _content_disposition_filename(filename: str) -> str:
    quoted_filename = quote(filename)
    return f"attachment; filename={filename}; filename*=UTF-8''{quoted_filename}"
