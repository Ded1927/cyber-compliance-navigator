from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.legal_act import LegalAct
    from app.models.organization_profile import OrganizationProfile


class RoadmapTemplateStep(Base):
    __tablename__ = "roadmap_template_steps"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    instructions_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    references_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    legal_act_id: Mapped[int | None] = mapped_column(
        ForeignKey("legal_acts.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    target_org_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    target_is_oki_okii: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    target_category: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_data_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    deadline_days: Mapped[int] = mapped_column(Integer, nullable=False, default=90)

    legal_act: Mapped["LegalAct | None"] = relationship(back_populates="template_steps")
    organization_tasks: Mapped[list["OrganizationTask"]] = relationship(
        back_populates="template",
        cascade="all, delete-orphan",
    )


class OrganizationTask(Base):
    __tablename__ = "organization_tasks"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "template_id",
            name="uq_organization_tasks_organization_template",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    organization_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("organization_profiles.public_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    template_id: Mapped[int] = mapped_column(
        ForeignKey("roadmap_template_steps.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")

    organization: Mapped["OrganizationProfile"] = relationship(
        back_populates="organization_tasks"
    )
    template: Mapped["RoadmapTemplateStep"] = relationship(
        back_populates="organization_tasks"
    )

    @property
    def title(self) -> str:
        return self.template.title

    @property
    def description(self) -> str:
        return self.template.description

    @property
    def guidance(self) -> str | None:
        return self.template.instructions_text

    @property
    def references(self) -> str | None:
        if self.template.references_text:
            return self.template.references_text

        if self.template.legal_act is None:
            return None

        reference_parts = [self.template.legal_act.title]
        if self.template.legal_act.official_link:
            reference_parts.append(self.template.legal_act.official_link)
        return "; ".join(reference_parts)

    @property
    def legal_basis(self) -> str:
        return self.template.legal_act.title if self.template.legal_act else "Внутрішня вимога"

    @property
    def deadline_days(self) -> int:
        return self.template.deadline_days


# Backwards-compatible alias for older imports while the API migrates to OrganizationTask.
RoadmapTask = OrganizationTask
