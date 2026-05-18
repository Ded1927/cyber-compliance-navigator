from enum import Enum

from pydantic import BaseModel, ConfigDict, model_validator

from app.schemas.organization_profile import OrganizationProfileResponse


class OrgType(str, Enum):
    STATE_BODY = "state_body"
    LOCAL_GOV = "local_gov"
    STATE_ENTERPRISE = "state_enterprise"
    PRIVATE = "private"


class CriticalityCategory(str, Enum):
    CAT_1 = "I"
    CAT_2 = "II"
    CAT_3 = "III"
    CAT_4 = "IV"


class DataType(str, Enum):
    DIR = "dir"
    IZOD = "izod"
    DIR_IZOD = "dir_izod"
    NONE = "none"


class QuestionnaireAnswers(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    org_type: OrgType
    is_oki_or_okii: bool
    category: CriticalityCategory | None = None
    data_type: DataType

    @model_validator(mode="after")
    def validate_oki_category(self) -> "QuestionnaireAnswers":
        if self.is_oki_or_okii and self.category is None:
            raise ValueError("category is required when is_oki_or_okii is true")

        if not self.is_oki_or_okii and self.category is not None:
            raise ValueError("category must be null when is_oki_or_okii is false")

        return self


class LegalActResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    number_date: str | None
    act_type: str
    status: str
    official_url: str | None
    short_explanation: str | None


class RoadmapItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    act_id: int
    step_name: str
    description: str | None
    status: int
    order_index: int
    legal_act: LegalActResponse


class RoadmapResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    organization_profile: OrganizationProfileResponse
    items: list[RoadmapItemResponse]
