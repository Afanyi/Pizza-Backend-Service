import pytest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base
import app.api.v1.endpoints.topping.crud as topping_crud

from app.api.v1.endpoints.topping.schemas import ToppingCreateSchema

# Create an SQLite in-memory database for testing
TEST_DATABASE_URL = 'sqlite:///:memory:'
engine = create_engine(TEST_DATABASE_URL, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Set up the database schema
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope='module')
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_topping_crud_operations(db_session):
    numbers_of_toppings_before = len(topping_crud.get_all_toppings(db_session))
    new_topping_name = 'Pepperoni'
    new_topping_price = Decimal('2.50')
    new_topping_description = 'Spicy'
    new_topping_stock = 100

    # Arrange: Instantiate a new topping Object
    topping = ToppingCreateSchema(
        name=new_topping_name,
        price=new_topping_price,  # Use Decimal for price
        description=new_topping_description,
        stock=new_topping_stock,
    )

    # Act: Add topping to database
    db_topping = topping_crud.create_topping(topping, db_session)
    created_topping_id = db_topping.id

    # Assert: One more topping in database
    toppings = topping_crud.get_all_toppings(db_session)
    assert len(toppings) == numbers_of_toppings_before + 1

    # Act: Re-read topping from database
    read_topping = topping_crud.get_topping_by_id(db_topping.id, db_session)

    # Assert: Correct topping was stored in database
    assert read_topping.id == created_topping_id
    assert read_topping.name == new_topping_name
    assert read_topping.price == new_topping_price
    assert read_topping.description == new_topping_description
    assert read_topping.stock == new_topping_stock

    # Act: Update Topping
    update_topping = ToppingCreateSchema(
        name='Double Pepperoni',
        price=Decimal('3.00'),
        description='Extra spicy and delicious pepperoni',
        stock=80,
    )
    updated_topping = topping_crud.update_topping(read_topping, update_topping, db_session)

    # Assert: Correct topping was stored in database
    assert updated_topping.name == 'Double Pepperoni'
    assert updated_topping.price == Decimal('3.00')
    assert updated_topping.description == 'Extra spicy and delicious pepperoni'
    assert updated_topping.stock == 80

    # Act: Delete topping
    topping_crud.delete_topping_by_id(updated_topping.id, db_session)

    # Assert: Correct number of toppings in database after deletion
    toppings = topping_crud.get_all_toppings(db_session)
    assert len(toppings) == numbers_of_toppings_before

    # Assert: Correct topping was deleted from database
    deleted_topping = topping_crud.get_topping_by_id(updated_topping.id, db_session)
    assert deleted_topping is None
