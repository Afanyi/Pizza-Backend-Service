import uuid
import pytest
from app.api.v1.endpoints.sauce.crud import (
    create_sauce,
    get_sauce_by_id,
    get_sauce_by_name,
    get_all_sauces,
    update_sauce,
    delete_sauce_by_id,
)
from app.api.v1.endpoints.sauce.schemas import SauceCreateSchema
from app.database.connection import SessionLocal


@pytest.fixture(scope='module')
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Helper function to clean up test data
def cleanup_sauce(name: str, db):
    existing_sauce = get_sauce_by_name(name, db)
    if existing_sauce:
        delete_sauce_by_id(existing_sauce.id, db)


def test_sauce_crud_operations(db):
    # Arrange: Define test data
    initial_data = {
        'name': 'Test Sauce',
        'description': 'A test sauce description.',
    }
    updated_data = {
        'name': 'Updated Sauce',
        'description': 'An updated sauce description.',
    }

    # Cleanup: Remove any existing test data
    cleanup_sauce(initial_data['name'], db)
    cleanup_sauce(updated_data['name'], db)

    # Act: Create a new sauce
    created_sauce = create_sauce(SauceCreateSchema(**initial_data), db)

    # Assert: Verify creation
    assert created_sauce.name == initial_data['name']
    assert created_sauce.description == initial_data['description']
    assert isinstance(created_sauce.id, uuid.UUID)

    # Act: Fetch the sauce by ID
    fetched_sauce = get_sauce_by_id(created_sauce.id, db)

    # Assert: Verify fetching by ID
    assert fetched_sauce is not None
    assert fetched_sauce.name == initial_data['name']

    # Act: Fetch the sauce by name
    fetched_by_name = get_sauce_by_name(initial_data['name'], db)

    # Assert: Verify fetching by name
    assert fetched_by_name is not None
    assert fetched_by_name.id == created_sauce.id

    # Act: Update the sauce
    updated_sauce = update_sauce(fetched_sauce, SauceCreateSchema(**updated_data), db)

    # Assert: Verify update
    assert updated_sauce.name == updated_data['name']
    assert updated_sauce.description == updated_data['description']

    # Act: Delete the sauce
    delete_sauce_by_id(updated_sauce.id, db)

    # Assert: Verify deletion
    assert get_sauce_by_id(updated_sauce.id, db) is None


def test_get_all_sauces(db):
    # Arrange: Define test data
    sauces = [
        {'name': 'Sauce 1', 'description': 'Tasty sauce.'},
        {'name': 'Sauce 2', 'description': 'Another tasty sauce.'},
    ]

    # Cleanup: Remove any existing test data
    for sauce in sauces:
        cleanup_sauce(sauce['name'], db)

    # Act: Create multiple sauces
    created_sauces = [
        create_sauce(SauceCreateSchema(**sauce), db) for sauce in sauces
    ]

    # Act: Fetch all sauces
    all_sauces = get_all_sauces(db)

    # Assert: Verify the created sauces are in the fetched list
    fetched_names = [sauce.name for sauce in all_sauces]
    for sauce in sauces:
        assert sauce['name'] in fetched_names

    # Cleanup: Delete the created sauces
    for created_sauce in created_sauces:
        delete_sauce_by_id(created_sauce.id, db)
