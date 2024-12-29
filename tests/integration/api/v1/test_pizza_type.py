import pytest
from decimal import Decimal
from uuid import uuid4
import app.api.v1.endpoints.topping.crud as topping_crud

from app.api.v1.endpoints.topping.schemas import ToppingCreateSchema
from app.api.v1.endpoints.pizza_type.crud import (
    create_pizza_type,
    get_pizza_type_by_id,
    delete_pizza_type_by_id,
    get_all_pizza_types,
    update_pizza_type,
    get_pizza_type_by_name,
    create_topping_quantity,
    get_topping_quantity_by_id,
)
from app.api.v1.endpoints.pizza_type.schemas import (
    PizzaTypeCreateSchema,
    PizzaTypeToppingQuantityCreateSchema,
)
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


def cleanup_topping(name: str, db):
    existing_topping = topping_crud.get_topping_by_name(name, db)
    if existing_topping:
        topping_crud.delete_topping_by_id(existing_topping.id, db)


def create_dummy_dough(db):
    initial_data = {
        'name': 'Test Dough',
        'price': Decimal('3.50'),
        'description': 'A test dough description.',
        'stock': 100,
    }
    return create_dough(DoughCreateSchema(**initial_data), db)


def create_dummy_topping(db):
    initial_data = {
        'name': 'Test Topping',
        'price': Decimal('3.50'),
        'description': 'A test topping description.',
        'stock': 100,
    }
    return topping_crud.create_topping(ToppingCreateSchema(**initial_data), db)


def test_pizza_type_crud_operations(db):
    # Step 1: Create a dummy dough entry
    dummy_dough_name = 'Test Dough'
    cleanup_dough(dummy_dough_name, db)
    dough = create_dummy_dough(db)

    # Step 2: Create a dummy topping
    dummy_topping_name = 'Test Topping'
    cleanup_topping(dummy_topping_name, db)
    topping = create_dummy_topping(db)

    # Step 3: Create a pizza type
    pizza_schema = PizzaTypeCreateSchema(
        name='Test Pizza',
        price=Decimal('12.99'),
        description='A test pizza',
        dough_id=dough.id,
    )
    created_pizza = create_pizza_type(pizza_schema, db)

    # Retrieve pizza by name
    pizza_retrieved_with_name = get_pizza_type_by_name('Test Pizza', db)

    # Assertions for pizza creation
    assert pizza_retrieved_with_name is not None, 'Failed to retrieve pizza by name.'
    assert pizza_retrieved_with_name.name == created_pizza.name
    assert created_pizza.id is not None, 'Pizza ID should not be None after creation.'
    assert created_pizza.price == Decimal('12.99'), 'Pizza price mismatch.'

    # Step 4: Retrieve the pizza type by ID
    fetched_pizza = get_pizza_type_by_id(created_pizza.id, db)

    # Assertions for pizza retrieval
    assert fetched_pizza is not None, 'Failed to retrieve pizza by ID.'
    assert fetched_pizza.name == 'Test Pizza', 'Pizza name mismatch.'

    # Step 5: Update the pizza type
    updated_schema = PizzaTypeCreateSchema(
        name='Updated Pizza',
        price=Decimal('15.99'),
        description='An updated test pizza',
        dough_id=dough.id,
    )
    updated_pizza = update_pizza_type(fetched_pizza, updated_schema, db)

    # Assertions for pizza update
    assert updated_pizza.name == 'Updated Pizza', 'Pizza name was not updated correctly.'
    assert updated_pizza.price == Decimal('15.99'), 'Pizza price mismatch.'

    # Step 6: Add a topping quantity
    topping_quantity_schema = PizzaTypeToppingQuantityCreateSchema(
        quantity=10,
        topping_id=topping.id,
    )
    topping_quantity = create_topping_quantity(updated_pizza, topping_quantity_schema, db)

    # Assertions for topping quantity creation
    assert topping_quantity is not None, 'Failed to create topping quantity.'
    assert topping_quantity.quantity == 10, 'Topping quantity mismatch.'
    assert topping_quantity.topping_id == topping.id, 'Topping ID mismatch.'

    # Verify topping quantity retrieval
    fetched_topping_quantity = get_topping_quantity_by_id(updated_pizza.id, topping.id, db)
    assert fetched_topping_quantity is not None, 'Failed to retrieve topping quantity.'
    assert fetched_topping_quantity.quantity == 10, 'Retrieved topping quantity mismatch.'

    # Step 7: Test retrieval of all pizza types
    all_pizzas = get_all_pizza_types(db)
    assert len(all_pizzas) >= 1, 'Failed to retrieve all pizza types.'
    assert any(pizza.name == 'Updated Pizza' for pizza in all_pizzas), 'Updated pizza not found.'

    # Step 8: Negative case - Retrieve non-existent pizza
    non_existent_pizza = get_pizza_type_by_id(uuid4(), db)
    assert non_existent_pizza is None, 'Non-existent pizza retrieval should return None.'

    # Cleanup
    delete_pizza_type_by_id(created_pizza.id, db)
    delete_dough_by_id(dough.id, db)
    topping_crud.delete_topping_by_id(topping.id, db)

    # Verify cleanup
    db.commit()
    assert get_pizza_type_by_id(created_pizza.id, db) is None, 'Pizza was not deleted during cleanup.'
    assert get_dough_by_name(dummy_dough_name, db) is None, 'Dough was not deleted during cleanup.'
    assert topping_crud.get_topping_by_name(dummy_topping_name, db) is None, 'Topping was not deleted during cleanup.'
