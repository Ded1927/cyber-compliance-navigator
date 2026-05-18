from enum import IntEnum
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.legal_act import LegalAct
    from app.models.user import User


class RoadmapStatus(IntEnum):
    NOT_STARTED = 0
    IDENTIFIED = 10
    PLANNED = 30
    IN_PROGRESS = 50
    REVIEW = 80
    DONE = 100


class RoadmapStatusType(TypeDecorator[RoadmapStatus]):
    impl = Integer
    cache_ok = True

    def process_bind_param(self, value: RoadmapStatus | int | None, dialect) -> int | None:
        if value is None:
            return None
        return int(RoadmapStatus(value))

    def process_result_value(self, value: int | None, dialect) -> RoadmapStatus | None:
        if value is None:
            return None
        return RoadmapStatus(value)


class RoadmapItem(Base):
    __tablename__ = "roadmap_items"
    __table_args__ = (
        CheckConstraint("status IN (0, 10, 30, 50, 80, 100)", name="ck_roadmap_items_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    act_id: Mapped[int] = mapped_column(
        ForeignKey("legal_acts.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    step_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[RoadmapStatus] = mapped_column(
        RoadmapStatusType(),
        nullable=False,
        default=RoadmapStatus.NOT_STARTED,
    )
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    user: Mapped["User"] = relationship(back_populates="roadmap_items")
    act: Mapped["LegalAct"] = relationship(back_populates="roadmap_items")
