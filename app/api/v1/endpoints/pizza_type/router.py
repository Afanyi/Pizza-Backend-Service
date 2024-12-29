import uuid
import logging
from typing import List, TypeVar

from fastapi import APIRouter, Depends, Request, Response, status, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

import app.api.v1.endpoints.dough.crud as dough_crud
import app.api.v1.endpoints.pizza_type.crud as pizza_type_crud
import app.api.v1.endpoints.topping.crud as topping_crud
from app.api.v1.endpoints.dough.schemas import DoughSchema
from app.api.v1.endpoints.pizza_type.schemas import (
    JoinedPizzaTypeQuantitySchema,
    PizzaTypeSchema,
    PizzaTypeCreateSchema,
    PizzaTypeToppingQuantityCreateSchema,
)
from app.database.connection import SessionLocal

# Configure logging
logging.basicConfig(level=logging.INFO)

ITEM_NOT_FOUND = 'Item not found'

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get('', response_model=List[PizzaTypeSchema], tags=['pizza_type'])
def get_all_pizza_types(db: Session = Depends(get_db)):
    logging.info('Fetching all pizza types.')
    pizza_types = pizza_type_crud.get_all_pizza_types(db)
    logging.info(f'Total pizza types fetched: {len(pizza_types)}')
    return pizza_types


@router.post('', response_model=PizzaTypeSchema, tags=['pizza_type'])
def create_pizza_type(
        pizza_type: PizzaTypeCreateSchema, request: Request,
        response: Response, db: Session = Depends(get_db),
):
    logging.info(f'Creating pizza type with name: {pizza_type.name}')
    pizza_type_found = pizza_type_crud.get_pizza_type_by_name(pizza_type.name, db)

    if pizza_type_found:
        logging.info(f'Pizza type already exists: {pizza_type_found.name} (ID: {pizza_type_found.id})')
        url = request.url_for('get_pizza_type', pizza_type_id=pizza_type_found.id)
        return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

    dough = dough_crud.get_dough_by_id(pizza_type.dough_id, db)
    if not dough:
        logging.warning(f'Dough with ID {pizza_type.dough_id} not found.')
        raise HTTPException(status_code=404, detail=ITEM_NOT_FOUND)

    new_pizza_type = pizza_type_crud.create_pizza_type(pizza_type, db)
    logging.info(f'Pizza type created successfully: {new_pizza_type.name} (ID: {new_pizza_type.id})')

    response.status_code = status.HTTP_201_CREATED
    return new_pizza_type


@router.put('/{pizza_type_id}', response_model=PizzaTypeSchema, tags=['pizza_type'])
def update_pizza_type(
        pizza_type_id: uuid.UUID,
        changed_pizza_type: PizzaTypeCreateSchema,
        request: Request,
        response: Response,
        db: Session = Depends(get_db),
):
    logging.info(f'Updating pizza type with ID: {pizza_type_id}')
    pizza_type_found = pizza_type_crud.get_pizza_type_by_id(pizza_type_id, db)
    updated_pizza_type = None

    if pizza_type_found:
        if pizza_type_found.name == changed_pizza_type.name:
            logging.info(f'No changes detected for pizza type: {pizza_type_found.name}')
            pizza_type_crud.update_pizza_type(pizza_type_found, changed_pizza_type, db)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            pizza_type_name_found = pizza_type_crud.get_pizza_type_by_name(changed_pizza_type.name, db)
            if pizza_type_name_found:
                logging.info(f'Pizza type name conflict: {changed_pizza_type.name} already exists.')
                url = request.url_for('get_pizza_type', pizza_type_id=pizza_type_name_found.id)
                return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)
            else:
                updated_pizza_type = pizza_type_crud.create_pizza_type(changed_pizza_type, db)
                logging.info(f'Pizza type updated successfully:'
                             f' {updated_pizza_type.name} (ID: {updated_pizza_type.id})')
                response.status_code = status.HTTP_201_CREATED
    else:
        logging.warning(f'Pizza type with ID {pizza_type_id} not found.')
        raise HTTPException(status_code=404, detail=ITEM_NOT_FOUND)

    return updated_pizza_type


@router.get('/{pizza_type_id}', response_model=PizzaTypeSchema, tags=['pizza_type'])
def get_pizza_type(
        pizza_type_id: uuid.UUID,
        db: Session = Depends(get_db),
):
    logging.info(f'Fetching pizza type with ID: {pizza_type_id}')
    pizza_type = pizza_type_crud.get_pizza_type_by_id(pizza_type_id, db)

    if not pizza_type:
        logging.warning(f'Pizza type with ID {pizza_type_id} not found.')
        raise HTTPException(status_code=404, detail=ITEM_NOT_FOUND)

    logging.info(f'Pizza type fetched successfully: {pizza_type.name} (ID: {pizza_type_id})')
    return pizza_type


@router.delete('/{pizza_type_id}', response_model=None, tags=['pizza_type'])
def delete_pizza_type(pizza_type_id: uuid.UUID,
                      db: Session = Depends(get_db),
                      ):
    logging.info(f'Deleting pizza type with ID: {pizza_type_id}')
    pizza_type = pizza_type_crud.get_pizza_type_by_id(pizza_type_id, db)

    if not pizza_type:
        logging.warning(f'Pizza type with ID {pizza_type_id} not found.')
        raise HTTPException(status_code=404, detail=ITEM_NOT_FOUND)

    pizza_type_crud.delete_pizza_type_by_id(pizza_type_id, db)
    logging.info(f'Pizza type with ID {pizza_type_id} deleted successfully.')
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Due to mypy error, this workaround is needed for Union
# see pull request https://github.com/python/mypy/pull/8779
# should be fixed in near future
MyPyEitherItem = TypeVar(
    'MyPyEitherItem',
    List[PizzaTypeToppingQuantityCreateSchema],
    List[JoinedPizzaTypeQuantitySchema],
    None,
)


@router.get(
    '/{pizza_type_id}/toppings',
    response_model=MyPyEitherItem,
    tags=['pizza_type'],
)
def get_pizza_type_toppings(
        pizza_type_id: uuid.UUID,
        response: Response,
        db: Session = Depends(get_db),
        join: bool = False,
):
    logging.info(f'Fetching toppings for pizza type ID: {pizza_type_id}')
    pizza_type = pizza_type_crud.get_pizza_type_by_id(pizza_type_id, db)

    if not pizza_type:
        logging.warning(f'Pizza type with ID {pizza_type_id} not found.')
        raise HTTPException(status_code=404, detail=ITEM_NOT_FOUND)

    toppings = pizza_type.toppings
    if join:
        toppings = pizza_type_crud.get_joined_topping_quantities_by_pizza_type(pizza_type.id, db)

    logging.info(f'Toppings fetched successfully for pizza type ID: {pizza_type_id}')
    return toppings


@router.post(
    '/{pizza_type_id}/toppings',
    response_model=PizzaTypeToppingQuantityCreateSchema,
    status_code=status.HTTP_201_CREATED,
    tags=['pizza_type'],
)
def create_pizza_type_topping(
        pizza_type_id: uuid.UUID,
        topping_quantity: PizzaTypeToppingQuantityCreateSchema,
        request: Request,
        response: Response,
        db: Session = Depends(get_db),
):
    logging.info(f'Adding topping to pizza type ID: {pizza_type_id}')
    pizza_type = pizza_type_crud.get_pizza_type_by_id(pizza_type_id, db)
    if not pizza_type:
        logging.warning(f'Pizza type with ID {pizza_type_id} not found.')
        raise HTTPException(status_code=404, detail=ITEM_NOT_FOUND)

    if not topping_crud.get_topping_by_id(topping_quantity.topping_id, db):
        logging.warning(f'Topping with ID {topping_quantity.topping_id} not found.')
        raise HTTPException(status_code=404, detail=ITEM_NOT_FOUND)

    topping_quantity_found = pizza_type_crud.get_topping_quantity_by_id(pizza_type_id, topping_quantity.topping_id, db)
    if topping_quantity_found:
        logging.info(f'Topping already exists for pizza type ID: {pizza_type_id}')
        url = request.url_for('get_pizza_type_toppings', pizza_type_id=topping_quantity_found.pizza_type_id)
        return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

    new_topping_quantity = pizza_type_crud.create_topping_quantity(pizza_type, topping_quantity, db)
    logging.info(f'Topping added successfully to pizza type ID: {pizza_type_id}')
    return new_topping_quantity


@router.get(
    '/{pizza_type_id}/dough',
    response_model=DoughSchema,
    tags=['pizza_type'],
)
def get_pizza_type_dough(
        pizza_type_id: uuid.UUID,
        response: Response,
        db: Session = Depends(get_db),
):
    logging.info(f'Fetching dough for pizza type ID: {pizza_type_id}')
    pizza_type = pizza_type_crud.get_pizza_type_by_id(pizza_type_id, db)

    if not pizza_type:
        logging.warning(f'Pizza type with ID {pizza_type_id} not found.')
        raise HTTPException(status_code=404, detail=ITEM_NOT_FOUND)

    dough = pizza_type.dough
    logging.info(f'Dough fetched successfully for pizza type ID: {pizza_type_id}')
    return dough
