from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.organization_profile import OrganizationProfile
    from app.models.roadmap_item import RoadmapItem
    from app.models.system_register_item import SystemRegisterItem


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    organization_profile: Mapped["OrganizationProfile | None"] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )
    roadmap_items: Mapped[list["RoadmapItem"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    system_register_items: Mapped[list["SystemRegisterItem"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
