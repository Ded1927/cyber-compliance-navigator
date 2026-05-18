from pydantic import BaseModel, ConfigDict, Field


class OrganizationProfileCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    org_type: str = Field(min_length=1, max_length=100)
    name_optional: str | None = Field(default=None, max_length=255)
    edrpou_optional: str | None = Field(default=None, min_length=8, max_length=16)
    is_oki_operator: bool = False
    criticality_category: int | None = Field(default=None, ge=1, le=4)


class OrganizationProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    org_type: str
    name_optional: str | None
    edrpou_optional: str | None
    is_oki_operator: bool
    criticality_category: int | None
