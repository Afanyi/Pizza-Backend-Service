# tests/test_user_crud.py

import pytest

import app.api.v1.endpoints.user.crud as user_crud
from app.api.v1.endpoints.user.crud import delete_user_by_id
from app.api.v1.endpoints.user.schemas import UserCreateSchema
from app.database.connection import SessionLocal


@pytest.fixture(scope='module')
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_user_create_read_update_delete(db):
    users = user_crud.get_all_users(db)
    for user in users:
        print('hi')
        delete_user_by_id(user.id, db)
    new_user_username = 'testuser'
    updated_username = 'updateduser'
    number_of_users_before = len(user_crud.get_all_users(db))

    # Arrange: Instantiate a new user object
    user_data = UserCreateSchema(username=new_user_username)

    # Act: Add user to database
    db_user = user_crud.create_user(user_data, db)
    created_user_id = db_user.id

    # Assert: One more user in database
    users = user_crud.get_all_users(db)

    assert len(users) == number_of_users_before + 1, 'User count should have increased by 1'

    # Act: Re-read user from database by ID
    read_user = user_crud.get_user_by_id(created_user_id, db)

    # Assert: Correct user was stored in database
    assert read_user is not None, 'User should exist in the database'
    assert read_user.id == created_user_id, 'User ID should match'
    assert read_user.username == new_user_username, 'Username should match'

    # Act: Re-read user from database by username
    read_user_by_username = user_crud.get_user_by_username(new_user_username, db)

    # Assert: Correct user was retrieved by username
    assert read_user_by_username is not None, 'User should be retrievable by username'
    assert read_user_by_username.id == created_user_id, 'User ID should match when retrieved by username'

    # Act: Update user's username using UserCreateSchema
    update_data = UserCreateSchema(username=updated_username)
    updated_user = user_crud.update_user(read_user, update_data, db)

    # Assert: User's username was updated
    assert updated_user.username == updated_username, '"User\"s username should be updated'

    # Verify that the old username no longer retrieves the user
    old_username_user = user_crud.get_user_by_username(new_user_username, db)
    assert old_username_user is None, 'Old username should no longer retrieve the user'

    # Verify that the new username retrieves the updated user
    new_username_user = user_crud.get_user_by_username(updated_username, db)
    assert new_username_user is not None, 'Updated username should retrieve the user'
    assert new_username_user.id == created_user_id, 'User ID should match for updated username'

    completed_orders = user_crud.get_order_history_of_user(updated_user.id, db)
    opened_orders = user_crud.get_open_orders_of_user(updated_user.id, db)
    not_completed_orders = user_crud.get_all_not_completed_orders(db)
    assert len(completed_orders) == 0, 'Order history should have one order'
    assert len(opened_orders) == 0, 'Order history should have one order'
    assert len(not_completed_orders) == 0, 'Order history should have one order'
    user_crud.delete_user_by_id(created_user_id, db)

    # Assert: Correct number of users in database after deletion
    users_after_deletion = user_crud.get_all_users(db)
    assert len(users_after_deletion) == number_of_users_before, 'User count should return to original after deletion'

    # Assert: Correct user was deleted from database
    deleted_user = user_crud.get_user_by_id(created_user_id, db)
    assert deleted_user is None, 'Deleted user should no longer exist in the database'
