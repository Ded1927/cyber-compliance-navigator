from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class SystemRegisterItem(Base):
    __tablename__ = "system_register_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    system_name: Mapped[str] = mapped_column(String(255), nullable=False)
    system_type: Mapped[str] = mapped_column(String(100), nullable=False)
    info_type: Mapped[str] = mapped_column(String(100), nullable=False)
    is_okii_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    auth_status: Mapped[str | None] = mapped_column(String(100), nullable=True)
    eval_status: Mapped[str | None] = mapped_column(String(100), nullable=True)

    user: Mapped["User"] = relationship(back_populates="system_register_items")
