import uuid
from pydantic import BaseModel


class SauceBaseSchema(BaseModel):
    name: str
    description: str

    class Config:
        orm_mode = True


class SauceCreateSchema(SauceBaseSchema):
    pass


class SauceSchema(SauceCreateSchema):
    id: uuid.UUID


class SauceListItemSchema(BaseModel):
    id: uuid.UUID
    name: str
    description: str

    class Config:
        orm_mode = True
