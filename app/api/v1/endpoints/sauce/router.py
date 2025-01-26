import uuid
import logging
from typing import List
from fastapi import APIRouter, Depends, Request, Response, status, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

import app.api.v1.endpoints.sauce.crud as sauce_crud
from app.api.v1.endpoints.sauce.schemas import SauceSchema, SauceCreateSchema, SauceListItemSchema
from app.database.connection import SessionLocal

ITEM_NOT_FOUND = 'Item not found'
logging.basicConfig(level=logging.INFO)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get('', response_model=List[SauceListItemSchema], tags=['sauce'])
def get_all_sauces(db: Session = Depends(get_db)):
    logging.info('Fetching all sauces.')
    sauces = sauce_crud.get_all_sauces(db)
    logging.info(f'Total sauces fetched: {len(sauces)}')
    return sauces


@router.post('', response_model=SauceSchema, status_code=status.HTTP_201_CREATED, tags=['sauce'])
def create_sauce(sauce: SauceCreateSchema, request: Request, db: Session = Depends(get_db)):
    logging.info(f'Attempting to create a new sauce: {sauce.name}')
    sauce_found = sauce_crud.get_sauce_by_name(sauce.name, db)

    if sauce_found:
        logging.info(f'Sauce already exists with ID: {sauce_found.id}. Redirecting to existing sauce.')
        url = request.url_for('get_sauce', sauce_id=sauce_found.id)
        return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

    new_sauce = sauce_crud.create_sauce(sauce, db)
    logging.info(f'Sauce created successfully with ID: {new_sauce.id}')
    return new_sauce


@router.put('/{sauce_id}', response_model=SauceSchema, tags=['sauce'])
def update_sauce(sauce_id: uuid.UUID, changed_sauce: SauceCreateSchema, db: Session = Depends(get_db)):
    logging.info(f'Attempting to update sauce with ID: {sauce_id}')
    sauce_found = sauce_crud.get_sauce_by_id(sauce_id, db)
    if not sauce_found:
        logging.warning(f'No sauce found with ID: {sauce_id}')
        raise HTTPException(status_code=404, detail=ITEM_NOT_FOUND)

    return sauce_crud.update_sauce(sauce_found, changed_sauce, db)


@router.get('/{sauce_id}', response_model=SauceSchema, tags=['sauce'])
def get_sauce(sauce_id: uuid.UUID, db: Session = Depends(get_db)):
    logging.info(f'Fetching sauce with ID: {sauce_id}')
    sauce = sauce_crud.get_sauce_by_id(sauce_id, db)
    if not sauce:
        logging.warning(f'Sauce with ID: {sauce_id} not found.')
        raise HTTPException(status_code=404, detail=ITEM_NOT_FOUND)
    return sauce


@router.delete('/{sauce_id}', response_model=None, tags=['sauce'])
def delete_sauce(sauce_id: uuid.UUID, db: Session = Depends(get_db)):
    logging.info(f'Attempting to delete sauce with ID: {sauce_id}')
    sauce = sauce_crud.get_sauce_by_id(sauce_id, db)
    if not sauce:
        logging.warning(f'Sauce with ID: {sauce_id} not found.')
        raise HTTPException(status_code=404, detail=ITEM_NOT_FOUND)
    sauce_crud.delete_sauce_by_id(sauce_id, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
