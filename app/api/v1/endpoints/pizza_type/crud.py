import uuid
import logging
from sqlalchemy.orm import Session
from app.api.v1.endpoints.pizza_type.schemas import (
    PizzaTypeCreateSchema,
    PizzaTypeToppingQuantityCreateSchema,
)
from app.database.models import PizzaType, PizzaTypeToppingQuantity

# Configure logging
logging.basicConfig(level=logging.INFO)


def create_pizza_type(schema: PizzaTypeCreateSchema, db: Session):
    logging.info(f'Creating a new pizza type with data: {schema.dict()}')
    try:
        # Create entity from schema
        entity = PizzaType(**schema.dict())
        db.add(entity)
        logging.info(f'Entity added to the session: {schema.dict()}')

        # Commit transaction
        db.commit()
        logging.info(f'Transaction committed successfully: {schema.dict()}')

        # Refresh the entity
        db.refresh(entity)
        logging.info(f'Entity refreshed: {entity}')

        # Log success
        logging.info(f'Pizza type created successfully with ID: {entity.id}')
    except Exception as e:
        # Rollback on error
        db.rollback()
        # Log error with schema information, ensuring safety
        logging.error(f'Failed to create pizza type. Error: {e}, Data: {schema.dict()}')
        raise

    return entity


def get_pizza_type_by_id(pizza_type_id: uuid.UUID, db: Session):
    logging.info(f'Fetching pizza type with ID: {pizza_type_id}')
    entity = db.query(PizzaType).filter(PizzaType.id == pizza_type_id).first()
    if entity:
        logging.info(f'Pizza type found: {entity.name} (ID: {pizza_type_id})')
    else:
        logging.warning(f'Pizza type with ID {pizza_type_id} not found.')
    return entity


def get_pizza_type_by_name(pizza_type_name: str, db: Session):
    logging.info(f'Fetching pizza type with name: {pizza_type_name}')
    entity = db.query(PizzaType).filter(PizzaType.name == pizza_type_name).first()
    if entity:
        logging.info(f'Pizza type found: {entity.name} (ID: {entity.id})')
    else:
        logging.warning(f'Pizza type with name {pizza_type_name} not found.')
    return entity


def get_all_pizza_types(db: Session):
    logging.info('Fetching all pizza types.')
    entities = db.query(PizzaType).all()
    logging.info(f'Total pizza types fetched: {len(entities)}')
    return entities


def update_pizza_type(pizza_type: PizzaType, changed_pizza_type: PizzaTypeCreateSchema, db: Session):
    logging.info(f'Updating pizza type with ID: {pizza_type.id}')
    for key, value in changed_pizza_type.dict().items():
        logging.debug(f'Updating field "{key}" to value "{value}"')
        setattr(pizza_type, key, value)

    db.commit()
    db.refresh(pizza_type)
    logging.info(f'Pizza type with ID {pizza_type.id} updated successfully.')
    return pizza_type


def delete_pizza_type_by_id(pizza_type_id: uuid.UUID, db: Session):
    logging.info(f'Deleting pizza type with ID: {pizza_type_id}')
    entity = get_pizza_type_by_id(pizza_type_id, db)
    if entity:
        db.delete(entity)
        db.commit()
        logging.info(f'Pizza type with ID {pizza_type_id} deleted successfully.')
    else:
        logging.warning(f'Pizza type with ID {pizza_type_id} not found, nothing to delete.')


def create_topping_quantity(
        pizza_type: PizzaType,
        schema: PizzaTypeToppingQuantityCreateSchema,
        db: Session,
):
    logging.info(f'Adding topping quantity to pizza type ID: {pizza_type.id} with data: {schema.dict()}')
    entity = PizzaTypeToppingQuantity(**schema.dict())
    pizza_type.toppings.append(entity)
    db.commit()
    db.refresh(pizza_type)
    logging.info(f'Topping quantity added successfully to pizza type ID: {pizza_type.id}')
    return entity


def get_topping_quantity_by_id(
        pizza_type_id: uuid.UUID,
        topping_id: uuid.UUID,
        db: Session,
):
    logging.info(f'Fetching topping quantity for topping ID: {topping_id} in pizza type ID: {pizza_type_id}')
    entity = db.query(PizzaTypeToppingQuantity) \
        .filter(PizzaTypeToppingQuantity.topping_id == topping_id,
                PizzaTypeToppingQuantity.pizza_type_id == pizza_type_id) \
        .first()
    if entity:
        logging.info(f'Topping quantity found for topping ID {topping_id} in pizza type ID {pizza_type_id}')
    else:
        logging.warning(f'Topping quantity not found for topping ID {topping_id} in pizza type ID {pizza_type_id}')
    return entity


def get_joined_topping_quantities_by_pizza_type(
        pizza_type_id: uuid.UUID,
        db: Session,
):
    logging.info(f'Fetching all topping quantities for pizza type ID: {pizza_type_id}')
    entities = db.query(PizzaTypeToppingQuantity) \
        .filter(PizzaTypeToppingQuantity.pizza_type_id == pizza_type_id).all()
    logging.info(f'Total topping quantities fetched for pizza type ID {pizza_type_id}: {len(entities)}')
    return entities
