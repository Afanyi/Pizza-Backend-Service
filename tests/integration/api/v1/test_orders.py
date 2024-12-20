# tests/integration/api/v1/test_orders.py

import pytest
from decimal import Decimal
import uuid
from uuid import UUID
from sqlalchemy.orm import Session

# Import CRUD operations and schemas
from app.api.v1.endpoints.user.crud import create_user, delete_user_by_id
from app.api.v1.endpoints.user.schemas import UserCreateSchema
from app.api.v1.endpoints.dough.crud import create_dough, delete_dough_by_id
from app.api.v1.endpoints.dough.schemas import DoughCreateSchema
from app.api.v1.endpoints.beverage.crud import create_beverage, delete_beverage_by_id
from app.api.v1.endpoints.beverage.schemas import BeverageCreateSchema
from app.api.v1.endpoints.pizza_type.crud import (
    create_pizza_type,
    delete_pizza_type_by_id,
)
from app.api.v1.endpoints.pizza_type.schemas import PizzaTypeCreateSchema
from app.api.v1.endpoints.order.crud import (
    create_order,
    get_order_by_id,
    get_all_orders,
    update_order_status,
    delete_order_by_id,
    add_pizza_to_order,
    create_beverage_quantity,
    get_price_of_order,
    get_pizza_by_id,
    get_all_pizzas_of_order,
    delete_pizza_from_order,
    get_beverage_quantity_by_id,
    get_joined_beverage_quantities_by_order,
    update_beverage_quantity_of_order,
    delete_beverage_from_order,
    get_orders_by_statuses,
)
from app.api.v1.endpoints.order.schemas import (
    OrderCreateSchema,
    OrderBeverageQuantityCreateSchema,
)
from app.database.models import OrderStatus, Pizza
from app.database.connection import SessionLocal


@pytest.fixture(scope='function')
def db_session():
    """
    Fixture for creating a test database session.
    Ensures that the session is properly closed after tests.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()  # Ensure any remaining transactions are committed
    except Exception:
        db.rollback()  # Rollback in case of exceptions
        raise
    finally:
        db.close()


@pytest.fixture(scope='function')
def dummy_user(db_session: Session):
    """
    Fixture for creating a dummy user for testing.
    """
    unique_username = f'test_user_{uuid.uuid4()}'
    user_schema = UserCreateSchema(username=unique_username)
    user = create_user(user_schema, db_session)
    db_session.commit()
    yield user
    # Cleanup is handled in the test's finally block


@pytest.fixture(scope='function')
def unique_dough(db_session: Session):
    """
    Fixture for creating a unique dough for testing purposes.
    Ensures that each test uses a unique dough to prevent data collisions.
    """
    dough_name = f'Test Dough {uuid.uuid4()}'
    initial_data = {
        'name': dough_name,
        'price': Decimal('3.50'),
        'description': 'A unique test dough description.',
        'stock': 100,
    }
    dough = create_dough(DoughCreateSchema(**initial_data), db_session)
    db_session.commit()
    yield dough
    # Cleanup is handled in the test's finally block


@pytest.fixture(scope='function')
def dummy_beverage(db_session: Session):
    """
    Fixture for creating a unique beverage for testing purposes.
    """
    beverage_name = f'Coke {uuid.uuid4()}'
    initial_data = {
        'name': beverage_name,
        'price': Decimal('3.50'),
        'description': 'A refreshing test beverage.',
        'stock': 100,
    }
    beverage = create_beverage(BeverageCreateSchema(**initial_data), db_session)
    db_session.commit()
    yield beverage
    # Cleanup is handled in the test's finally block


def delete_pizza_by_id(pizza_id: UUID, db: Session):
    """
    Helper function to delete a pizza by its ID.
    """
    pizza = db.query(Pizza).filter(Pizza.id == pizza_id).first()
    if pizza:
        db.delete(pizza)
        db.commit()


def test_order_lifecycle(db_session: Session, dummy_user, unique_dough, dummy_beverage):
    """
    Integration test that covers create, read, update, and delete operations for an order.
    Ensures that referential integrity is maintained by deleting dependent records first.
    """
    # Initialize variables to track created entities
    created_order = None
    fetched_order = None
    updated_order = None
    pizza_type = None
    added_pizza = None
    added_beverage = None

    try:
        # Step 1: Create an order
        address_data = {
            'street': 'Main St',
            'house_number': '42',
            'post_code': '12345',
            'town': 'Test Shire',
            'country': 'Test Land',
            'first_name': 'John',
            'last_name': 'Doe',
        }
        order_schema = OrderCreateSchema(user_id=dummy_user.id, address=address_data)
        created_order = create_order(order_schema, db_session)

        # Verify creation
        assert created_order.id
        assert created_order.user_id == dummy_user.id, 'Order user_id .'
        assert created_order.order_status == OrderStatus.TRANSMITTED

        # Step 2: Read the order
        fetched_order = get_order_by_id(created_order.id, db_session)
        assert fetched_order, 'Fetched order should not be None.'
        assert fetched_order.id == created_order.id

        # Step 3: Update the order status
        updated_status = OrderStatus.PREPARING
        updated_order = update_order_status(fetched_order, updated_status, db_session)
        assert updated_order.order_status == updated_status, 'Order status was not updated correctly.'

        # Step 4: Add a pizza to the order
        pizza_schema = PizzaTypeCreateSchema(
            name=f'Test Pizza {uuid.uuid4()}',
            price=Decimal('12.99'),
            description='A test pizza',
            dough_id=unique_dough.id,
        )
        pizza_type = create_pizza_type(pizza_schema, db_session)
        added_pizza = add_pizza_to_order(fetched_order, pizza_type, db_session)

        # Verify the pizza was added
        assert added_pizza.pizza_type_id == pizza_type.id, 'Pizza type ID does not match the added pizza type.'

        # Step 5: Add a beverage to the order
        beverage_schema = OrderBeverageQuantityCreateSchema(beverage_id=dummy_beverage.id, quantity=3)
        added_beverage = create_beverage_quantity(fetched_order, beverage_schema, db_session)

        # Verify the beverage was added
        assert added_beverage.beverage_id == dummy_beverage.id
        assert added_beverage.quantity == 3, 'Beverage quantity does not match the expected value.'

        # Step 6: Calculate the total price
        expected_price = Decimal('12.99') + (Decimal('3.50') * 3)
        total_price = get_price_of_order(fetched_order.id, db_session)
        assert total_price == expected_price, f'Expected total price {expected_price}, but got {total_price}.'

        statuses = [updated_order.order_status]
        order_from_status = get_orders_by_statuses(statuses, db_session)
        assert order_from_status[0].order_status == updated_order.order_status, 'Order status get order'

    finally:
        # Cleanup test data in the correct order to avoid ForeignKeyViolation

        # Delete the beverage quantity first
        if added_beverage:
            # Assuming there's a delete function for beverage quantities
            # If not, implement it similarly to delete_pizza_by_id
            delete_beverage_from_order(fetched_order.id, added_beverage.beverage_id, db_session)

        # Delete the added pizza
        if added_pizza:
            delete_pizza_from_order(fetched_order, added_pizza.id, db_session)

        # Delete the pizza type
        if pizza_type:
            delete_pizza_type_by_id(pizza_type.id, db_session)

        # Delete the order
        if fetched_order:
            delete_order_by_id(fetched_order.id, db_session)

        # Delete the beverage
        if dummy_beverage:
            delete_beverage_by_id(dummy_beverage.id, db_session)

        # Delete the dough
        if unique_dough:
            delete_dough_by_id(unique_dough.id, db_session)

        # Delete the user
        if dummy_user:
            delete_user_by_id(dummy_user.id, db_session)


def test_order_crud_additional(db_session: Session, dummy_user, unique_dough, dummy_beverage):
    """
    Additional integration test to cover remaining CRUD operations in crud.py:
    - get_all_orders
    - get_pizza_by_id
    - get_all_pizzas_of_order
    - delete_pizza_from_order
    - get_beverage_quantity_by_id
    - get_joined_beverage_quantities_by_order
    - update_beverage_quantity_of_order
    - delete_beverage_from_order
    """
    # Initialize variables to track created entities
    created_order = None
    pizza_type_1 = None
    pizza_type_2 = None
    added_pizza_1 = None
    added_pizza_2 = None
    added_beverage_1 = None
    added_beverage_2 = None
    second_beverage = None  # To track the second beverage

    try:
        # Step 1: Create an order
        address_data = {
            'street': 'Second St',
            'house_number': '24',
            'post_code': '54321',
            'town': 'Sample Town',
            'country': 'Sample Country',
            'first_name': 'Jane',
            'last_name': 'Smith',
        }
        order_schema = OrderCreateSchema(user_id=dummy_user.id, address=address_data)
        created_order = create_order(order_schema, db_session)
        db_session.commit()

        # Step 2: Add multiple pizzas to the order
        pizza_schema_1 = PizzaTypeCreateSchema(
            name=f'Test Pizza 1 {uuid.uuid4()}',
            price=Decimal('10.00'),
            description='First test pizza',
            dough_id=unique_dough.id,
        )
        pizza_type_1 = create_pizza_type(pizza_schema_1, db_session)
        added_pizza_1 = add_pizza_to_order(created_order, pizza_type_1, db_session)
        db_session.commit()

        pizza_schema_2 = PizzaTypeCreateSchema(
            name=f'Test Pizza 2 {uuid.uuid4()}',
            price=Decimal('15.00'),
            description='Second test pizza',
            dough_id=unique_dough.id,
        )
        pizza_type_2 = create_pizza_type(pizza_schema_2, db_session)
        added_pizza_2 = add_pizza_to_order(created_order, pizza_type_2, db_session)
        db_session.commit()

        # Step 3: Add multiple beverages to the order
        # Add the first beverage
        beverage_schema_1 = OrderBeverageQuantityCreateSchema(beverage_id=dummy_beverage.id, quantity=2)
        added_beverage_1 = create_beverage_quantity(created_order, beverage_schema_1, db_session)
        db_session.commit()

        # Create and add a second, distinct beverage
        second_beverage_schema = BeverageCreateSchema(
            name=f'Sprite {uuid.uuid4()}',
            price=Decimal('3.75'),
            description='A different refreshing test beverage.',
            stock=100,
        )
        second_beverage = create_beverage(second_beverage_schema, db_session)
        beverage_schema_2 = OrderBeverageQuantityCreateSchema(beverage_id=second_beverage.id, quantity=5)
        added_beverage_2 = create_beverage_quantity(created_order, beverage_schema_2, db_session)
        db_session.commit()

        # Step 4: Fetch all orders and verify
        all_orders = get_all_orders(db_session)
        assert len(all_orders) >= 1
        assert any(
            order.id == created_order.id for order in all_orders)

        # Step 5: Fetch a pizza by ID and verify
        fetched_pizza = get_pizza_by_id(added_pizza_1.id, db_session)
        assert fetched_pizza, 'Fetched pizza should not be None.'
        assert fetched_pizza.id == added_pizza_1.id

        # Step 6: Fetch all pizzas of the order and verify
        all_pizzas = get_all_pizzas_of_order(created_order, db_session)
        assert len(all_pizzas) == 2, 'There should be two pizzas associated with the order.'
        pizza_ids = [pizza.id for pizza in all_pizzas]
        assert added_pizza_1.id in pizza_ids and added_pizza_2.id in pizza_ids

        # Step 7: Update beverage quantity
        new_quantity = 4
        updated_beverage = update_beverage_quantity_of_order(
            order_id=created_order.id,
            beverage_id=added_beverage_1.beverage_id,
            new_quantity=new_quantity,
            db=db_session,
        )
        assert updated_beverage.quantity == new_quantity, 'Beverage quantity was not updated correctly.'
        db_session.commit()

        # Step 8: Fetch beverage quantity by ID and verify
        fetched_beverage = get_beverage_quantity_by_id(
            order_id=created_order.id,
            beverage_id=added_beverage_1.beverage_id,
            db=db_session,
        )
        assert fetched_beverage, 'Fetched beverage quantity should not be None.'
        assert fetched_beverage.quantity == new_quantity, 'Fetched beverage quantity does not match the updated value.'

        # Step 9: Fetch all beverage quantities of the order and verify
        all_beverages = get_joined_beverage_quantities_by_order(created_order.id, db_session)
        assert len(all_beverages) == 2, 'There should be two beverage quantities associated with the order.'
        beverage_ids = [bev.beverage_id for bev in all_beverages]
        assert added_beverage_1.beverage_id in beverage_ids and added_beverage_2.beverage_id in beverage_ids
        db_session.commit()

    finally:
        # Cleanup test data in the correct order to avoid ForeignKeyViolation

        # Delete beverage quantities
        if added_beverage_1:
            delete_beverage_from_order(created_order.id, added_beverage_1.beverage_id, db_session)
        if added_beverage_2:
            delete_beverage_from_order(created_order.id, added_beverage_2.beverage_id, db_session)
        db_session.commit()

        # Delete the second beverage
        if second_beverage:
            delete_beverage_by_id(second_beverage.id, db_session)
        db_session.commit()

        # Delete pizzas
        if added_pizza_1:
            delete_pizza_from_order(created_order, added_pizza_1.id, db_session)
        if added_pizza_2:
            delete_pizza_from_order(created_order, added_pizza_2.id, db_session)
        db_session.commit()

        # Delete pizza types
        if pizza_type_1:
            delete_pizza_type_by_id(pizza_type_1.id, db_session)
        if pizza_type_2:
            delete_pizza_type_by_id(pizza_type_2.id, db_session)
        db_session.commit()

        # Delete the order
        if created_order:
            delete_order_by_id(created_order.id, db_session)
        db_session.commit()

        # Delete the first beverage
        if dummy_beverage:
            delete_beverage_by_id(dummy_beverage.id, db_session)
        db_session.commit()

        # Delete the dough
        if unique_dough:
            delete_dough_by_id(unique_dough.id, db_session)
        db_session.commit()

        # Delete the user
        if dummy_user:
            delete_user_by_id(dummy_user.id, db_session)
        db_session.commit()
