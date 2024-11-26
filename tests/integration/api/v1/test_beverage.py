import uuid
import pytest
from decimal import Decimal

from app.api.v1.endpoints.beverage.crud import (
    create_beverage,
    get_beverage_by_id,
    get_beverage_by_name,
    get_all_beverages,
    update_beverage,
    delete_beverage_by_id,
)
from app.api.v1.endpoints.beverage.schemas import BeverageCreateSchema
from app.database.connection import SessionLocal


# Fixture for database connection
@pytest.fixture(scope='module')
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_beverage_crud_operations(db):
    # Arrange: Define initial and updated test data
    initial_data = {
        'name': 'Test Beverage',
        'price': Decimal('3.50'),
        'description': 'A refreshing test beverage.',
        'stock': 100,
    }
    updated_data = {
        'name': 'Updated Beverage',
        'price': Decimal('4.00'),
        'description': 'An updated refreshing beverage.',
        'stock': 90,
    }

    # Act: Create a new beverage
    created_beverage = create_beverage(BeverageCreateSchema(**initial_data), db)

    # Assert: Verify creation
    assert created_beverage.name == initial_data['name']
    assert created_beverage.price == initial_data['price']
    assert created_beverage.description == initial_data['description']
    assert created_beverage.stock == initial_data['stock']
    assert isinstance(created_beverage.id, uuid.UUID)

    # Act: Fetch beverage by ID
    fetched_beverage = get_beverage_by_id(created_beverage.id, db)

    # Assert: Verify fetching by ID
    assert fetched_beverage is not None
    assert fetched_beverage.name == initial_data['name']

    # Act: Fetch beverage by name
    fetched_by_name = get_beverage_by_name(initial_data['name'], db)

    # Assert: Verify fetching by name
    assert fetched_by_name is not None
    assert fetched_by_name.id == created_beverage.id

    # Act: Update the beverage
    updated_beverage = update_beverage(fetched_beverage, BeverageCreateSchema(**updated_data), db)

    # Assert: Verify update
    assert updated_beverage.name == updated_data['name']
    assert updated_beverage.price == updated_data['price']
    assert updated_beverage.description == updated_data['description']
    assert updated_beverage.stock == updated_data['stock']

    # Act: Delete the beverage
    delete_beverage_by_id(updated_beverage.id, db)

    # Assert: Verify deletion
    assert get_beverage_by_id(updated_beverage.id, db) is None


# Test fetching all beverages
def test_get_all_beverages(db):
    # Cleanup: Remove any existing test data
    for beverage_name in ['Beverage 1', 'Beverage 2']:
        existing_beverage = get_beverage_by_name(beverage_name, db)
        if existing_beverage:
            delete_beverage_by_id(existing_beverage.id, db)

    # Arrange: Add multiple beverages
    beverage1 = create_beverage(
        BeverageCreateSchema(
            name='Beverage 1',
            price=Decimal('1.50'),
            description='A tasty beverage.',
            stock=50,
        ),
        db,
    )
    beverage2 = create_beverage(
        BeverageCreateSchema(
            name='Beverage 2',
            price=Decimal('2.50'),
            description='A refreshing beverage.',
            stock=75,
        ),
        db,
    )

    # Act: Fetch all beverages
    beverages = get_all_beverages(db)

    # Assert: Ensure the added beverages are in the list
    assert len(beverages) >= 2
    beverage_names = [b.name for b in beverages]
    assert 'Beverage 1' in beverage_names
    assert 'Beverage 2' in beverage_names

    # Cleanup: Delete added beverages
    delete_beverage_by_id(beverage1.id, db)
    delete_beverage_by_id(beverage2.id, db)
