import uuid
import logging
from sqlalchemy.orm import Session
from app.api.v1.endpoints.sauce.schemas import SauceCreateSchema
from app.database.models import Sauce

logging.basicConfig(level=logging.INFO)


def create_sauce(schema: SauceCreateSchema, db: Session):
    try:
        logging.info(f'Attempting to create a sauce with data: {schema.dict()}')
        entity = Sauce(**schema.dict())
        db.add(entity)
        db.commit()
        logging.info(f'Sauce created successfully with ID: {entity.id}')
        return entity
    except Exception as e:
        logging.error(f'Error occurred while creating sauce: {e}')
        raise e


def get_sauce_by_id(sauce_id: uuid.UUID, db: Session):
    logging.info(f'Fetching sauce with ID: {sauce_id}')
    entity = db.query(Sauce).filter(Sauce.id == sauce_id).first()
    if entity:
        logging.info(f'Sauce found: {entity.name} (ID: {sauce_id})')
    else:
        logging.warning(f'No sauce found with ID: {sauce_id}')
    return entity


def get_sauce_by_name(sauce_name: str, db: Session):
    logging.info(f'Fetching sauce with name: {sauce_name}')
    entity = db.query(Sauce).filter(Sauce.name == sauce_name).first()
    if entity:
        logging.info(f'Sauce found: {entity.name} (ID: {entity.id})')
    else:
        logging.warning(f'No sauce found with name: {sauce_name}')
    return entity


def get_all_sauces(db: Session):
    logging.info('Fetching all sauces from the database.')
    sauces = db.query(Sauce).all()
    logging.info(f'Total sauces fetched: {len(sauces)}')
    return sauces


def update_sauce(sauce: Sauce, changed_sauce: SauceCreateSchema, db: Session):
    try:
        logging.info(f'Updating sauce with ID: {sauce.id}')
        for key, value in changed_sauce.dict().items():
            logging.debug(f'Updating field \"{key}\" to value \"{value}\"')
            setattr(sauce, key, value)
        db.commit()
        db.refresh(sauce)
        logging.info(f'Sauce updated successfully: {sauce.name} (ID: {sauce.id})')
        return sauce
    except Exception as e:
        logging.error(f'Error occurred while updating sauce with ID {sauce.id}: {e}')
        raise e


def delete_sauce_by_id(sauce_id: uuid.UUID, db: Session):
    try:
        logging.info(f'Attempting to delete sauce with ID: {sauce_id}')
        entity = get_sauce_by_id(sauce_id, db)
        if entity:
            db.delete(entity)
            db.commit()
            logging.info(f'Sauce with ID {sauce_id} deleted successfully.')
        else:
            logging.warning(f'No sauce found with ID: {sauce_id}, nothing to delete.')
    except Exception as e:
        logging.error(f'Error occurred while deleting sauce with ID {sauce_id}: {e}')
        raise e
