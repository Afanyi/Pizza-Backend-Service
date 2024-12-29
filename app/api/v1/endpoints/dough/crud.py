import uuid
import logging
from sqlalchemy.orm import Session
from app.api.v1.endpoints.dough.schemas import DoughCreateSchema
from app.database.models import Dough

# Configure the logger
logging.basicConfig(level=logging.INFO)


def create_dough(schema: DoughCreateSchema, db: Session):
    try:
        logging.info(f'Attempting to create a dough with data: {schema.dict()}')
        entity = Dough(**schema.dict())
        db.add(entity)
        db.commit()
        logging.info(f'Dough created successfully with ID: {entity.id}')
        return entity
    except Exception as e:
        logging.error(f'Error occurred while creating dough: {e}')
        raise e


def get_dough_by_id(dough_id: uuid.UUID, db: Session):
    logging.info(f'Fetching dough with ID: {dough_id}')
    entity = db.query(Dough).filter(Dough.id == dough_id).first()
    if entity:
        logging.info(f'Dough found: {entity.name} (ID: {dough_id})')
    else:
        logging.warning(f'No dough found with ID: {dough_id}')
    return entity


def get_dough_by_name(dough_name: str, db: Session):
    logging.info(f'Fetching dough with name: {dough_name}')
    entity = db.query(Dough).filter(Dough.name == dough_name).first()
    if entity:
        logging.info(f'Dough found: {entity.name} (ID: {entity.id})')
    else:
        logging.warning(f'No dough found with name: {dough_name}')
    return entity


def get_all_doughs(db: Session):
    logging.info('Fetching all doughs from the database.')
    doughs = db.query(Dough).all()
    logging.info(f'Total doughs fetched: {len(doughs)}')
    return doughs


def update_dough(dough: Dough, changed_dough: DoughCreateSchema, db: Session):
    try:
        logging.info(f'Updating dough with ID: {dough.id}')
        for key, value in changed_dough.dict().items():
            logging.debug(f"Updating field \'{key}\' to value \'{value}\'")
            setattr(dough, key, value)
        db.commit()
        db.refresh(dough)
        logging.info(f'Dough updated successfully: {dough.name} (ID: {dough.id})')
        return dough
    except Exception as e:
        logging.error(f'Error occurred while updating dough with ID {dough.id}: {e}')
        raise e


def delete_dough_by_id(dough_id: uuid.UUID, db: Session):
    try:
        logging.info(f'Attempting to delete dough with ID: {dough_id}')
        entity = get_dough_by_id(dough_id, db)
        if entity:
            db.delete(entity)
            db.commit()
            logging.info(f'Dough with ID {dough_id} deleted successfully.')
        else:
            logging.warning(f'No dough found with ID: {dough_id}, nothing to delete.')
    except Exception as e:
        logging.error(f'Error occurred while deleting dough with ID {dough_id}: {e}')
        raise e
