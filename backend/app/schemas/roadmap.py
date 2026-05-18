from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LegalActCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: str | None = None
    official_link: str | None = Field(default=None, max_length=2048)
    date_adopted: date | None = None


class LegalActUpdate(LegalActCreate):
    pass


class LegalActResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    official_link: str | None
    date_adopted: date | None


class RoadmapTemplateStepCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    instructions_text: str | None = None
    references_text: str | None = None
    legal_act_id: int | None = None
    target_org_type: str | None = Field(default=None, max_length=100)
    target_is_oki_okii: bool | None = None
    target_category: int | None = Field(default=None, ge=1, le=4)
    target_data_type: str | None = Field(default=None, max_length=50)
    deadline_days: int = Field(gt=0, default=90)


class RoadmapTemplateStepUpdate(RoadmapTemplateStepCreate):
    pass


class RoadmapTemplateStepResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    instructions_text: str | None
    references_text: str | None
    legal_act_id: int | None
    legal_act: LegalActResponse | None = None
    target_org_type: str | None
    target_is_oki_okii: bool | None
    target_category: int | None
    target_data_type: str | None
    deadline_days: int


class OrganizationTaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    template_id: int
    title: str
    description: str
    guidance: str | None
    references: str | None
    status: str
    legal_basis: str
    deadline_days: int


class OrganizationTaskStatusUpdate(BaseModel):
    status: str = Field(min_length=1, max_length=50)


class RoadmapTaskUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    guidance: str | None = None
    references: str | None = None
    legal_basis: str | None = Field(default=None, max_length=255)
    deadline_days: int = Field(gt=0)


# Backwards-compatible names used by the current frontend/API layer.
RoadmapTaskCreate = RoadmapTemplateStepCreate
RoadmapTaskResponse = OrganizationTaskResponse
