import logging
import uuid
from sqlalchemy.orm import Session
from app.api.v1.endpoints.user.schemas import UserCreateSchema
from app.database.models import Order, User

# Configure logging
logging.basicConfig(level=logging.INFO)


def create_user(schema: UserCreateSchema, db: Session):
    logging.info(f'Creating a new user with username: {schema.username}')
    entity = User(**schema.dict())
    db.add(entity)
    db.commit()
    logging.info(f'User created successfully with username: {entity.username} (ID: {entity.id})')
    return entity


def get_user_by_username(username: str, db: Session):
    logging.info(f'Fetching user with username: {username}')
    entity = db.query(User).filter(User.username == username).first()
    if entity:
        logging.info(f'User found: {entity.username} (ID: {entity.id})')
    else:
        logging.warning(f'User with username {username} not found.')
    return entity


def get_user_by_id(user_id: uuid.UUID, db: Session):
    logging.info(f'Fetching user with ID: {user_id}')
    entity = db.query(User).filter(User.id == user_id).first()
    if entity:
        logging.info(f'User found: {entity.username} (ID: {user_id})')
    else:
        logging.warning(f'User with ID {user_id} not found.')
    return entity


def get_all_users(db: Session):
    logging.info('Fetching all users.')
    entities = db.query(User).all()
    if entities:
        logging.info(f'Total users fetched: {len(entities)}')
    else:
        logging.warning('No users found in the database.')
    return entities


def update_user(user: User, changed_user: UserCreateSchema, db: Session):
    logging.info(f'Updating user with ID: {user.id}')
    for key, value in changed_user.dict().items():
        logging.debug(f'Updating field {key} to value {value}')
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    logging.info(f'User with ID {user.id} updated successfully.')
    return user


def delete_user_by_id(user_id: uuid.UUID, db: Session):
    logging.info(f'Deleting user with ID: {user_id}')
    entity = get_user_by_id(user_id, db)
    if entity:
        db.delete(entity)
        db.commit()
        logging.info(f'User with ID {user_id} deleted successfully.')
    else:
        logging.warning(f'User with ID {user_id} not found, nothing to delete.')


def get_order_history_of_user(user_id: uuid.UUID, db: Session) -> list[Order]:
    logging.info(f'Fetching completed order history for user ID: {user_id}')
    entities = db.query(Order).filter(Order.user_id == user_id, Order.order_status == 'COMPLETED').all()
    if entities:
        logging.info(f'Total completed orders fetched for user ID {user_id}: {len(entities)}')
    else:
        logging.warning(f'No completed orders found for user ID {user_id}.')
    return entities


def get_open_orders_of_user(user_id: uuid.UUID, db: Session):
    logging.info(f'Fetching open orders for user ID: {user_id}')
    entities = db.query(Order).filter(Order.user_id == user_id, Order.order_status != 'COMPLETED').all()
    if entities:
        logging.info(f'Total open orders fetched for user ID {user_id}: {len(entities)}')
    else:
        logging.warning(f'No open orders found for user ID {user_id}.')
    return entities


def get_all_not_completed_orders(db: Session):
    logging.info('Fetching all not completed orders.')
    entities = db.query(Order).filter(Order.order_status != 'COMPLETED').all()
    if entities:
        logging.info(f'Total not completed orders fetched: {len(entities)}')
    else:
        logging.warning('No not completed orders found.')
    return entities
