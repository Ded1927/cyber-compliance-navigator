from pydantic import BaseModel, Field


class CisoOrderContext(BaseModel):
    organization_name: str = Field(min_length=1, max_length=255)
    ciso_full_name: str = Field(min_length=1, max_length=255)
    department: str = Field(min_length=1, max_length=255)

    def to_template_context(self) -> dict:
        return self.model_dump()
