import uuid
import logging
from typing import List

from fastapi import APIRouter, Depends, Request, Response, status, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

import app.api.v1.endpoints.dough.crud as dough_crud
from app.api.v1.endpoints.dough.schemas import DoughSchema, DoughCreateSchema, DoughListItemSchema
from app.database.connection import SessionLocal

ITEM_NOT_FOUND = 'Item not found'

# Configure the logger
logging.basicConfig(level=logging.INFO)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get('', response_model=List[DoughListItemSchema], tags=['dough'])
def get_all_doughs(db: Session = Depends(get_db)):
    logging.info('Fetching all doughs.')
    doughs = dough_crud.get_all_doughs(db)
    logging.info(f'Total doughs fetched: {len(doughs)}')
    return doughs


@router.post('', response_model=DoughSchema, status_code=status.HTTP_201_CREATED, tags=['dough'])
def create_dough(dough: DoughCreateSchema,
                 request: Request,
                 db: Session = Depends(get_db),
                 ):
    logging.info(f'Attempting to create a new dough: {dough.name}')
    dough_found = dough_crud.get_dough_by_name(dough.name, db)

    if dough_found:
        logging.info(f'Dough already exists with ID: {dough_found.id}. Redirecting to existing dough.')
        url = request.url_for('get_dough', dough_id=dough_found.id)
        return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

    new_dough = dough_crud.create_dough(dough, db)
    logging.info(f'Dough created successfully with ID: {new_dough.id}')
    return new_dough


@router.put('/{dough_id}', response_model=DoughSchema, tags=['dough'])
def update_dough(
        dough_id: uuid.UUID,
        changed_dough: DoughCreateSchema,
        request: Request,
        response: Response,
        db: Session = Depends(get_db),
):
    logging.info(f'Attempting to update dough with ID: {dough_id}')
    dough_found = dough_crud.get_dough_by_id(dough_id, db)
    updated_dough = None

    if dough_found:
        if dough_found.name == changed_dough.name:
            logging.info(f'No changes detected for dough with ID: {dough_id}')
            dough_crud.update_dough(dough_found, changed_dough, db)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            logging.info(f'Updating dough name from {dough_found.name} to {changed_dough.name}')
            dough_name_found = dough_crud.get_dough_by_name(changed_dough.name, db)
            if dough_name_found:
                logging.info(f'Conflict with existing dough ID: {dough_name_found.id}. Redirecting.')
                url = request.url_for('get_dough', dough_id=dough_name_found.id)
                return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)
            else:
                updated_dough = dough_crud.create_dough(changed_dough, db)
                logging.info(f'Dough updated successfully with new ID: {updated_dough.id}')
                response.status_code = status.HTTP_201_CREATED
    else:
        logging.warning(f'No dough found with ID: {dough_id}')
        raise HTTPException(status_code=404, detail=ITEM_NOT_FOUND)

    return updated_dough


@router.get('/{dough_id}', response_model=DoughSchema, tags=['dough'])
def get_dough(dough_id: uuid.UUID,
              db: Session = Depends(get_db),
              ):
    logging.info(f'Fetching dough with ID: {dough_id}')
    dough = dough_crud.get_dough_by_id(dough_id, db)

    if not dough:
        logging.warning(f'Dough with ID: {dough_id} not found.')
        raise HTTPException(status_code=404, detail=ITEM_NOT_FOUND)

    logging.info(f'Dough fetched successfully: {dough.name} (ID: {dough_id})')
    return dough


@router.delete('/{dough_id}', response_model=None, tags=['dough'])
def delete_dough(dough_id: uuid.UUID, db: Session = Depends(get_db)):
    logging.info(f'Attempting to delete dough with ID: {dough_id}')
    dough = dough_crud.get_dough_by_id(dough_id, db)

    if not dough:
        logging.warning(f'Dough with ID: {dough_id} not found. Cannot delete.')
        raise HTTPException(status_code=404, detail=ITEM_NOT_FOUND)

    dough_crud.delete_dough_by_id(dough_id, db)
    logging.info(f'Dough with ID: {dough_id} deleted successfully.')
    return Response(status_code=status.HTTP_204_NO_CONTENT)
