from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.roadmap import OrganizationTask


class OrganizationProfile(Base):
    __tablename__ = "organization_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    public_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        default=uuid4,
        unique=True,
        index=True,
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    org_type: Mapped[str] = mapped_column(String(100), nullable=False)
    name_optional: Mapped[str | None] = mapped_column(String(255), nullable=True)
    edrpou_optional: Mapped[str | None] = mapped_column(String(16), nullable=True)
    is_oki_operator: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    criticality_category: Mapped[int | None] = mapped_column(Integer, nullable=True)

    user: Mapped["User"] = relationship(back_populates="organization_profile")
    organization_tasks: Mapped[list["OrganizationTask"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    @property
    def roadmap_tasks(self) -> list["OrganizationTask"]:
        return self.organization_tasks
