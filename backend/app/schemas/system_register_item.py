from pydantic import BaseModel, ConfigDict, Field


class SystemRegisterItemCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    system_name: str = Field(min_length=1, max_length=255)
    system_type: str = Field(min_length=1, max_length=100)
    info_type: str = Field(min_length=1, max_length=100)
    is_okii_system: bool = False
    auth_status: str | None = Field(default=None, max_length=100)
    eval_status: str | None = Field(default=None, max_length=100)


class SystemRegisterItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    system_name: str
    system_type: str
    info_type: str
    is_okii_system: bool
    auth_status: str | None
    eval_status: str | None
