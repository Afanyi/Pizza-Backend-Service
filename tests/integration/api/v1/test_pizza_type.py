import pytest
from decimal import Decimal
from app.api.v1.endpoints.pizza_type.crud import (
    create_pizza_type,
    get_pizza_type_by_id,
    delete_pizza_type_by_id,
)
from app.api.v1.endpoints.pizza_type.schemas import PizzaTypeCreateSchema
from app.api.v1.endpoints.dough.crud import (
    create_dough,
    get_dough_by_name,
    delete_dough_by_id,
)
from app.api.v1.endpoints.dough.schemas import DoughCreateSchema
from app.database.connection import SessionLocal


@pytest.fixture(scope='module')
def db():

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def cleanup_dough(name: str, db):

    existing_dough = get_dough_by_name(name, db)
    if existing_dough:
        delete_dough_by_id(existing_dough.id, db)


def create_dummy_dough(db):
    initial_data = {
        'name': 'Test Dough',
        'price': Decimal('3.50'),
        'description': 'A test dough description.',
        'stock': 100,
    }
    return create_dough(DoughCreateSchema(**initial_data), db)


def test_pizza_type_crud_operations(db):
    # Step 1: Create a dummy dough entry
    dummy_dough_name = 'Test Dough'
    cleanup_dough(dummy_dough_name, db)  # Ensure a clean start
    dough = create_dummy_dough(db)

    # Step 2: Create a pizza type
    pizza_schema = PizzaTypeCreateSchema(
        name='Test Pizza',
        price=Decimal('12.99'),
        description='A test pizza',
        dough_id=dough.id,
    )
    created_pizza = create_pizza_type(pizza_schema, db)

    # Assertions for pizza creation
    assert created_pizza.id is not None, 'Pizza ID should not be None after creation.'
    assert created_pizza.name == 'Test Pizza', 'Pizza name does not match expected value.'
    assert created_pizza.price == Decimal('12.99'), 'Pizza price does not match expected value.'

    # Step 3: Retrieve the pizza type by ID
    fetched_pizza = get_pizza_type_by_id(created_pizza.id, db)

    # Assertions for pizza retrieval
    assert fetched_pizza is not None, 'Failed to retrieve pizza by ID.'
    assert fetched_pizza.name == 'Test Pizza', 'Retrieved pizza name does not match expected value.'

    # Step 4: Cleanup - Delete the pizza and dough
    delete_pizza_type_by_id(created_pizza.id, db)
    delete_dough_by_id(dough.id, db)

    # Verify cleanup
    db.commit()
    assert get_pizza_type_by_id(created_pizza.id, db) is None, 'Pizza was not deleted during cleanup.'
    assert get_dough_by_name(dummy_dough_name, db) is None, 'Dough was not deleted during cleanup.'
