import uuid
import pytest
from decimal import Decimal
from app.api.v1.endpoints.dough.crud import (
    create_dough,
    get_dough_by_id,
    get_dough_by_name,
    get_all_doughs,
    update_dough,
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


# Helper function to clean up test data
def cleanup_dough(name: str, db):
    existing_dough = get_dough_by_name(name, db)
    if existing_dough:
        delete_dough_by_id(existing_dough.id, db)


def test_dough_crud_operations(db):
    # Arrange: Define test data
    initial_data = {
        'name': 'Test Dough',
        'price': Decimal('3.50'),
        'description': 'A test dough description.',
        'stock': 100,
    }
    updated_data = {
        'name': 'Updated Dough',
        'price': Decimal('4.00'),
        'description': 'An updated dough description.',
        'stock': 90,
    }

    # Cleanup: Remove any existing test data
    cleanup_dough(initial_data['name'], db)
    cleanup_dough(updated_data['name'], db)

    # Act: Create a new dough
    created_dough = create_dough(DoughCreateSchema(**initial_data), db)

    # Assert: Verify creation
    assert created_dough.name == initial_data['name']
    assert created_dough.price == initial_data['price']
    assert created_dough.description == initial_data['description']
    assert created_dough.stock == initial_data['stock']
    assert isinstance(created_dough.id, uuid.UUID)

    # Act: Fetch the dough by ID
    fetched_dough = get_dough_by_id(created_dough.id, db)

    # Assert: Verify fetching by ID
    assert fetched_dough is not None
    assert fetched_dough.name == initial_data['name']

    # Act: Fetch the dough by name
    fetched_by_name = get_dough_by_name(initial_data['name'], db)

    # Assert: Verify fetching by name
    assert fetched_by_name is not None
    assert fetched_by_name.id == created_dough.id

    # Act: Update the dough
    updated_dough = update_dough(fetched_dough, DoughCreateSchema(**updated_data), db)

    # Assert: Verify update
    assert updated_dough.name == updated_data['name']
    assert updated_dough.price == updated_data['price']
    assert updated_dough.description == updated_data['description']
    assert updated_dough.stock == updated_data['stock']

    # Act: Delete the dough
    delete_dough_by_id(updated_dough.id, db)

    # Assert: Verify deletion
    assert get_dough_by_id(updated_dough.id, db) is None


def test_get_all_doughs(db):
    # Arrange: Define test data
    doughs = [
        {'name': 'Dough 1', 'price': Decimal('1.50'), 'description': 'Tasty dough.', 'stock': 50},
        {'name': 'Dough 2', 'price': Decimal('2.50'), 'description': 'Another tasty dough.', 'stock': 75},
    ]

    # Cleanup: Remove any existing test data
    for dough in doughs:
        cleanup_dough(dough['name'], db)

    # Act: Create multiple doughs
    created_doughs = [
        create_dough(DoughCreateSchema(**dough), db) for dough in doughs
    ]

    # Act: Fetch all doughs
    all_doughs = get_all_doughs(db)

    # Assert: Verify the created doughs are in the fetched list
    fetched_names = [dough.name for dough in all_doughs]
    for dough in doughs:
        assert dough['name'] in fetched_names

    # Cleanup: Delete the created doughs
    for created_dough in created_doughs:
        delete_dough_by_id(created_dough.id, db)
