import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base
from app.api.v1.endpoints.order.address.schemas import AddressCreateSchema
from app.api.v1.endpoints.order.address.crud import (
    create_address,
    get_address_by_id,
    delete_address_by_id,
    update_address,
    get_all_addresses,
)


# Test database setup
@pytest.fixture(scope='module')
def test_db():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(bind=engine)
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = testing_session_local()
    yield db
    db.close()


def test_address_crud_operations(test_db):
    # Create Address
    address_data = AddressCreateSchema(
        street='Main St',
        post_code='12345',
        house_number=10,
        country='USA',
        town='Anytown',
        first_name='John',
        last_name='Doe',
    )
    new_address = create_address(address_data, test_db)
    assert new_address.id is not None
    assert new_address.street == 'Main St'

    # Get Address by ID
    fetched_address = get_address_by_id(new_address.id, test_db)
    assert fetched_address.id == new_address.id

    # Update Address
    updated_data = AddressCreateSchema(
        street='Updated St',
        post_code='54321',
        house_number=20,
        country='USA',
        town='Newtown',
        first_name='Jane',
        last_name='Doe',
    )
    updated_address = update_address(fetched_address, updated_data, test_db)
    assert updated_address.street == 'Updated St'
    assert updated_address.first_name == 'Jane'

    # Get All Addresses
    all_addresses = get_all_addresses(test_db)
    assert len(all_addresses) == 1

    # Delete Address
    delete_address_by_id(updated_address.id, test_db)
    deleted_address = get_address_by_id(updated_address.id, test_db)
    assert deleted_address is None
