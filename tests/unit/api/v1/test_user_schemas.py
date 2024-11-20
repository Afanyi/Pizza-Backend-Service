import uuid
import random
import string
import pytest

from app.api.v1.endpoints.user.schemas import UserSchema, UserBaseSchema, UserCreateSchema


def generate_random_username(length=8):
    """Generate a random username with letters and digits."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_random_password(length=12):
    """Generate a random password with letters, digits, and special characters."""
    characters = string.ascii_letters + string.digits + '!@#$%^&*()'
    return ''.join(random.choices(characters, k=length))


@pytest.fixture(scope='module')
def user_dict():
    return {
        'id': uuid.uuid4(),
        'username': generate_random_username(),
        'password': generate_random_password(),
    }


def test_user_create_schema(user_dict):
    schema = UserCreateSchema(**user_dict)
    assert schema.username == user_dict['username']

    assert not hasattr(schema, 'id')


def test_user_base_schema(user_dict):
    schema = UserBaseSchema(**user_dict)
    assert schema.username == user_dict['username']

    assert not hasattr(schema, 'id')


def test_schema(user_dict):
    schema = UserSchema(**user_dict)
    assert schema.username == user_dict['username']
