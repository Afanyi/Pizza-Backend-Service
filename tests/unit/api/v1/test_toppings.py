import uuid
from decimal import Decimal
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unicodedata import decimal

from app.database.models import Base
from app.api.v1.endpoints.topping.schemas import ToppingCreateSchema
from app.api.v1.endpoints.topping.crud import (
    create_topping,
    get_topping_by_id,
    get_topping_by_name,
    get_all_toppings,
    update_topping,
    delete_topping_by_id,
)

# Setup an in-memory SQLite database for testing
DATABASE_URL = 'sqlite:///:memory:'

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture(scope='function')
def db():
    # Create all tables before each test
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    # Drop all tables after each test
    Base.metadata.drop_all(bind=engine)


def test_create_topping(db):
    schema = ToppingCreateSchema(
        name='Cheese',
        price=decimal('1.0'),
        description='Delicious cheese',
        stock=100)
    topping = create_topping(schema, db)
    assert topping.id is not None
    assert topping.name == 'Cheese'
    assert topping.price == decimal('1.0')
    assert topping.description == 'Delicious cheese'
    assert topping.stock == 100


def test_get_topping_by_id(db):
    schema = ToppingCreateSchema(
        name='Pepperoni',
        price=1.5,
        description='Spicy pepperoni',
        stock=50)
    topping = create_topping(schema, db)
    retrieved_topping = get_topping_by_id(topping.id, db)
    assert retrieved_topping.id == topping.id
    assert retrieved_topping.name == 'Pepperoni'
    assert retrieved_topping.stock == 50


def test_get_topping_by_id_not_exists(db):
    fake_id = uuid.uuid4()
    topping = get_topping_by_id(fake_id, db)
    assert topping is None


def test_get_topping_by_name(db):
    schema = ToppingCreateSchema(
        name='Mushrooms',
        price=1.2,
        description='Fresh mushrooms',
        stock=30)
    topping = create_topping(schema, db)
    retrieved_topping = get_topping_by_name('Mushrooms', db)
    assert retrieved_topping.id == topping.id
    assert retrieved_topping.name == 'Mushrooms'
    assert retrieved_topping.stock == 30


def test_get_topping_by_name_not_exists(db):
    topping = get_topping_by_name('Nonexistent', db)
    assert topping is None


def test_get_all_toppings_empty(db):
    toppings = get_all_toppings(db)
    assert toppings == []


def test_get_all_toppings(db):
    schema1 = ToppingCreateSchema(
        name='Olives',
        price=1.0,
        description='Black olives',
        stock=40)
    schema2 = ToppingCreateSchema(
        name='Onions',
        price=0.8,
        description='Red onions',
        stock=35)
    create_topping(schema1, db)
    create_topping(schema2, db)
    toppings = get_all_toppings(db)
    assert len(toppings) == 2
    names = [topping.name for topping in toppings]
    assert 'Olives' in names
    assert 'Onions' in names


def test_update_topping(db):
    schema = ToppingCreateSchema(
        name='Pineapple',
        price=1.0,
        description='Sweet pineapple',
        stock=20)
    topping = create_topping(schema, db)
    updated_schema = ToppingCreateSchema(
        name='Pineapple',
        price=Decimal('1.20'),
        description='Juicy pineapple',
        stock=25)
    updated_topping = update_topping(topping, updated_schema, db)
    assert updated_topping.price == Decimal('1.20')
    assert updated_topping.description == 'Juicy pineapple'
    assert updated_topping.stock == 25


def test_delete_topping_by_id(db):
    schema = ToppingCreateSchema(
        name='Bacon',
        price=1.5,
        description='Crispy bacon',
        stock=60)
    topping = create_topping(schema, db)
    topping_id = topping.id
    delete_topping_by_id(topping_id, db)
    retrieved_topping = get_topping_by_id(topping_id, db)
    assert retrieved_topping is None


def test_delete_topping_by_id_not_exists(db):
    fake_id = uuid.uuid4()
    delete_topping_by_id(fake_id, db)
    # Ensure no exceptions are raised and function completes
