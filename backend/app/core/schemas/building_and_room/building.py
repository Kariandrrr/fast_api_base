from uuid import UUID

from pydantic import Field, BaseModel

from .. import BaseSchema


class BuildingBase(BaseSchema):
    name: str = Field(
        ...,
        description="Название",
        min_length=1,
        max_length=50,
        pattern=r"^[A-ZА-Я]",
    )
    address: str = Field(..., description="Адрес", min_length=10, max_length=150)


class BuildingCreate(BuildingBase):
    pass


class BuildingUpdate(BaseModel):
    name: str | None = Field(
        None,
        description="Название",
        min_length=1,
        max_length=50,
        pattern=r"^[A-ZА-Я]",
    )
    address: str | None = Field(
        None, description="Адрес", min_length=10, max_length=150
    )


class BuildingResponse(BaseSchema, BuildingBase):
    id: UUID = Field(..., description="Уникальный идентификатор")


class BuildingBrief(BaseSchema):
    id: UUID = Field(..., description="ID здания")
    name: str = Field(..., description="Название")
    address: str = Field(..., description="Адрес")
