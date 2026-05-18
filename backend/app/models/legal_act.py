from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.roadmap_item import RoadmapItem
    from app.models.roadmap import RoadmapTemplateStep


class LegalAct(Base):
    __tablename__ = "legal_acts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    official_link: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    date_adopted: Mapped[date | None] = mapped_column(Date, nullable=True)
    number_date: Mapped[str | None] = mapped_column(String(255), nullable=True)
    act_type: Mapped[str] = mapped_column(String(100), nullable=False, default="law")
    status: Mapped[str] = mapped_column(String(100), nullable=False, default="active")
    official_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    short_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)

    roadmap_items: Mapped[list["RoadmapItem"]] = relationship(back_populates="act")
    template_steps: Mapped[list["RoadmapTemplateStep"]] = relationship(
        back_populates="legal_act"
    )
