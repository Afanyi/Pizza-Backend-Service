import uuid
import logging
from sqlalchemy.orm import Session
from app.api.v1.endpoints.beverage.schemas import BeverageCreateSchema
from app.database.models import Beverage

# Configure the logger
logging.basicConfig(level=logging.INFO)


def create_beverage(schema: BeverageCreateSchema, db: Session):
    try:
        logging.info(f'Attempting to create a beverage with data: {schema.dict()}')
        entity = Beverage(**schema.dict())
        db.add(entity)
        db.commit()
        logging.info(f'Beverage created successfully with ID: {entity.id}')
        return entity
    except Exception as e:
        logging.error(f'Error occurred while creating beverage: {e}')
        raise e


def get_beverage_by_id(beverage_id: uuid.UUID, db: Session):
    logging.info(f'Fetching beverage with ID: {beverage_id}')
    entity = db.query(Beverage).filter(Beverage.id == beverage_id).first()
    if entity:
        logging.info(f'Beverage found: {entity.name} (ID: {beverage_id})')
    else:
        logging.warning(f'No beverage found with ID: {beverage_id}')
    return entity


def get_beverage_by_name(beverage_name: str, db: Session):
    logging.info(f'Fetching beverage with name: {beverage_name}')
    entity = db.query(Beverage).filter(Beverage.name == beverage_name).first()
    if entity:
        logging.info(f'Beverage found: {entity.name} (ID: {entity.id})')
    else:
        logging.warning(f'No beverage found with name: {beverage_name}')
    return entity


def get_all_beverages(db: Session):
    logging.info('Fetching all beverages from the database.')
    beverages = db.query(Beverage).all()
    logging.info(f'Total beverages fetched: {len(beverages)}')
    return beverages


def update_beverage(beverage: Beverage, changed_beverage: BeverageCreateSchema, db: Session):
    try:
        logging.info(f'Updating beverage with ID: {beverage.id}')
        for key, value in changed_beverage.dict().items():
            logging.debug(f"Updating field \'{key}\' to value \'{value}\'")
            setattr(beverage, key, value)
        db.commit()
        db.refresh(beverage)
        logging.info(f'Beverage updated successfully: {beverage.name} (ID: {beverage.id})')
        return beverage
    except Exception as e:
        logging.error(f'Error occurred while updating beverage with ID {beverage.id}: {e}')
        raise e


def delete_beverage_by_id(beverage_id: uuid.UUID, db: Session):
    try:
        logging.info(f'Attempting to delete beverage with ID: {beverage_id}')
        entity = get_beverage_by_id(beverage_id, db)
        if entity:
            db.delete(entity)
            db.commit()
            logging.info(f'Beverage with ID {beverage_id} deleted successfully.')
        else:
            logging.warning(f'No beverage found with ID: {beverage_id}, nothing to delete.')
    except Exception as e:
        logging.error(f'Error occurred while deleting beverage with ID {beverage_id}: {e}')
        raise e
