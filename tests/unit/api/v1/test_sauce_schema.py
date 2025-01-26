import uuid

import pytest

from app.api.v1.endpoints.sauce.schemas import SauceBaseSchema, SauceCreateSchema, SauceSchema


@pytest.fixture(scope='module')
def sauce_dict():
    return {
        'id': uuid.uuid4(),
        'name': 'Marinara',
        'description': 'Classic tomato sauce with garlic and herbs.',
    }


def test_sauce_create_schema(sauce_dict):
    schema = SauceCreateSchema(**sauce_dict)
    assert schema.name == sauce_dict['name']
    assert schema.description == sauce_dict['description']

    # Ensure that `id` is not part of `SauceCreateSchema`
    assert not hasattr(schema, 'id')


def test_sauce_base_schema(sauce_dict):
    schema = SauceBaseSchema(**sauce_dict)
    assert schema.name == sauce_dict['name']
    assert schema.description == sauce_dict['description']

    # Ensure that `id` is not part of `SauceBaseSchema`
    assert not hasattr(schema, 'id')


def test_sauce_schema(sauce_dict):
    schema = SauceSchema(**sauce_dict)
    assert schema.id == sauce_dict['id']
    assert schema.name == sauce_dict['name']
    assert schema.description == sauce_dict['description']
