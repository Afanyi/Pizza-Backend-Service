import pytest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base
from app.api.v1.endpoints.topping.crud import (
    create_topping,
    get_topping_by_id,
    update_topping,
    delete_topping_by_id,
)
from app.api.v1.endpoints.topping.schemas import ToppingCreateSchema

# Create an SQLite in-memory database for testing
TEST_DATABASE_URL = 'sqlite:///:memory:'
engine = create_engine(TEST_DATABASE_URL, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Set up the database schema
Base.metadata.create_all(bind=engine)


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_topping_crud_operations(db_session):

    # **Step 1: Create a new topping**
    create_schema = ToppingCreateSchema(
        name='Pepperoni',
        price=Decimal('2.50'),  # Use Decimal for price
        description='Spicy and delicious pepperoni',
        stock=100,
    )
    created_topping = create_topping(create_schema, db_session)

    # Verify the topping is created
    assert created_topping.id is not None
    assert created_topping.name == 'Pepperoni'
    assert created_topping.price == Decimal('2.50')
    assert created_topping.description == 'Spicy and delicious pepperoni'
    assert created_topping.stock == 100

    # **Step 2: Read the topping by ID**
    retrieved_topping = get_topping_by_id(created_topping.id, db_session)

    # Verify the retrieved topping matches the created one
    assert retrieved_topping is not None
    assert retrieved_topping.name == 'Pepperoni'
    assert retrieved_topping.price == Decimal('2.50')

    # **Step 3: Update the topping**
    update_schema = ToppingCreateSchema(
        name='Double Pepperoni',
        price=Decimal('3.00'),
        description='Extra spicy and delicious pepperoni',
        stock=80,
    )
    updated_topping = update_topping(retrieved_topping, update_schema, db_session)

    # Verify the topping is updated
    assert updated_topping.name == 'Double Pepperoni'
    assert updated_topping.price == Decimal('3.00')
    assert updated_topping.description == 'Extra spicy and delicious pepperoni'
    assert updated_topping.stock == 80

    # **Step 4: Delete the topping**
    delete_topping_by_id(updated_topping.id, db_session)

    # Verify the topping is deleted
    deleted_topping = get_topping_by_id(updated_topping.id, db_session)
    assert deleted_topping is None
