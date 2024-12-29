import uuid
import logging
from typing import List

from fastapi import APIRouter, Depends, Request, Response, status, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

import app.api.v1.endpoints.beverage.crud as beverage_crud
from app.api.v1.endpoints.beverage.schemas import BeverageSchema, BeverageCreateSchema, BeverageListItemSchema
from app.database.connection import SessionLocal

ITEM_NOT_FOUND = 'Item not found'

# Configure the logger
logging.basicConfig(level=logging.INFO)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter()


@router.get('', response_model=List[BeverageListItemSchema], tags=['beverage'])
def get_all_beverages(db: Session = Depends(get_db)):
    logging.info('Fetching all beverages.')
    beverages = beverage_crud.get_all_beverages(db)
    logging.info(f'Total beverages fetched: {len(beverages)}')
    return beverages


@router.post('', response_model=BeverageSchema, status_code=status.HTTP_201_CREATED, tags=['beverage'])
def create_beverage(beverage: BeverageCreateSchema,
                    request: Request,
                    db: Session = Depends(get_db)):
    logging.info(f'Attempting to create a new beverage: {beverage.name}')
    beverage_found = beverage_crud.get_beverage_by_name(beverage.name, db)

    if beverage_found:
        logging.info(f'Beverage already exists with ID: {beverage_found.id}. Redirecting to existing beverage.')
        url = request.url_for('get_beverage', beverage_id=beverage_found.id)
        return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

    new_beverage = beverage_crud.create_beverage(beverage, db)
    logging.info(f'Beverage created successfully with ID: {new_beverage.id}')
    return new_beverage


@router.put('/{beverage_id}', response_model=BeverageSchema, tags=['beverage'])
def update_beverage(
        beverage_id: uuid.UUID,
        changed_beverage: BeverageCreateSchema,
        request: Request,
        response: Response,
        db: Session = Depends(get_db)):
    logging.info(f'Attempting to update beverage with ID: {beverage_id}')
    beverage_found = beverage_crud.get_beverage_by_id(beverage_id, db)

    if beverage_found:
        if beverage_found.name == changed_beverage.name:
            logging.info(f'No changes detected for beverage with ID: {beverage_id}')
            beverage_crud.update_beverage(beverage_found, changed_beverage, db)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            logging.info(f'Updating beverage name from {beverage_found.name} to {changed_beverage.name}')
            beverage_name_found = beverage_crud.get_beverage_by_name(changed_beverage.name, db)
            if beverage_name_found:
                logging.info(f'Conflict with existing beverage ID: {beverage_name_found.id}. Redirecting.')
                url = request.url_for('get_beverage', beverage_id=beverage_name_found.id)
                return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)
            else:
                updated_beverage = beverage_crud.create_beverage(changed_beverage, db)
                logging.info(f'Beverage updated successfully with new ID: {updated_beverage.id}')
                response.status_code = status.HTTP_201_CREATED
    else:
        logging.warning(f'No beverage found with ID: {beverage_id}')
        raise HTTPException(status_code=404, detail=ITEM_NOT_FOUND)

    return updated_beverage


@router.get('/{beverage_id}', response_model=BeverageSchema, tags=['beverage'])
def get_beverage(
        beverage_id: uuid.UUID,
        db: Session = Depends(get_db)):
    logging.info(f'Fetching beverage with ID: {beverage_id}')
    beverage = beverage_crud.get_beverage_by_id(beverage_id, db)

    if not beverage:
        logging.warning(f'Beverage with ID: {beverage_id} not found.')
        raise HTTPException(status_code=404, detail=ITEM_NOT_FOUND)

    logging.info(f'Beverage fetched successfully: {beverage.name} (ID: {beverage_id})')
    return beverage


@router.delete('/{beverage_id}', response_model=None, tags=['beverage'])
def delete_beverage(
        beverage_id: uuid.UUID,
        db: Session = Depends(get_db)):
    logging.info(f'Attempting to delete beverage with ID: {beverage_id}')
    beverage = beverage_crud.get_beverage_by_id(beverage_id, db)

    if not beverage:
        logging.warning(f'Beverage with ID: {beverage_id} not found. Cannot delete.')
        raise HTTPException(status_code=404, detail=ITEM_NOT_FOUND)

    beverage_crud.delete_beverage_by_id(beverage_id, db)
    logging.info(f'Beverage with ID: {beverage_id} deleted successfully.')
    return Response(status_code=status.HTTP_204_NO_CONTENT)
