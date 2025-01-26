import uuid
from typing import Optional
from pydantic import BaseModel

from app.api.v1.endpoints.topping.schemas import ToppingBaseSchema


class PizzaTypeBaseSchema(BaseModel):
    name: str
    price: float
    description: str
    default_sauce_id: Optional[uuid.UUID] = None

    class Config:
        orm_mode = True


class PizzaTypeCreateSchema(PizzaTypeBaseSchema):
    dough_id: uuid.UUID


class PizzaTypeSchema(PizzaTypeBaseSchema):
    id: uuid.UUID


class PizzaTypeToppingQuantityBaseSchema(BaseModel):
    quantity: int

    class Config:
        orm_mode = True


class PizzaTypeToppingQuantityCreateSchema(PizzaTypeToppingQuantityBaseSchema):
    topping_id: uuid.UUID


class JoinedPizzaTypeQuantitySchema(PizzaTypeBaseSchema, ToppingBaseSchema):
    pass
