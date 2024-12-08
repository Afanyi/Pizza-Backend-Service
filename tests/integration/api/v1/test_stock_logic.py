import uuid
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, Beverage
from app.api.v1.endpoints.order.stock_logic.stock_beverage_crud import beverage_is_available, change_stock_of_beverage


# Test database setup
@pytest.fixture(scope='module')
def test_db():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(bind=engine)
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = testing_session_local()
    yield db
    db.close()


def test_beverage_stock_logic(test_db):
    # Setup test data
    beverage_id = uuid.uuid4()
    beverage = Beverage(id=beverage_id, name='Coke', stock=10, price=2.5)
    test_db.add(beverage)
    test_db.commit()

    # Test beverage availability
    assert beverage_is_available(beverage_id, 5, test_db)  # Should be True
    assert not beverage_is_available(beverage_id, 15, test_db)  # Should be False
    assert beverage_is_available(beverage_id, 10, test_db)  # Should be True

    # Test stock change
    assert change_stock_of_beverage(beverage_id, -5, test_db)  # Reduce stock
    updated_beverage = test_db.query(Beverage).filter(Beverage.id == beverage_id).first()
    assert updated_beverage.stock == 5

    assert not change_stock_of_beverage(beverage_id, -10, test_db)  # Can't reduce below 0
    updated_beverage = test_db.query(Beverage).filter(Beverage.id == beverage_id).first()
    assert updated_beverage.stock == 5

    assert change_stock_of_beverage(beverage_id, 5, test_db)  # Increase stock
    updated_beverage = test_db.query(Beverage).filter(Beverage.id == beverage_id).first()
    assert updated_beverage.stock == 10
