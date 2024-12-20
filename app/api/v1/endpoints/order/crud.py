import uuid
import logging
from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.api.v1.endpoints.order.address.crud import create_address
from app.api.v1.endpoints.order.schemas import (
    JoinedPizzaPizzaTypeSchema, OrderBeverageQuantityCreateSchema, OrderCreateSchema,
)
from app.database.models import Order, Pizza, PizzaType, OrderBeverageQuantity, Beverage, OrderStatus

# Configure logger
logging.basicConfig(level=logging.INFO)


def create_order(schema: OrderCreateSchema, db: Session):
    logging.info(f'Creating order for user_id: {schema.user_id}')
    address = create_address(schema.address, db)
    order = Order(user_id=schema.user_id)
    order.address = address
    order.order_status = OrderStatus.TRANSMITTED
    db.add(order)
    db.commit()
    logging.info(f'Order created successfully with ID: {order.id}')
    return order


def get_order_by_id(order_id: uuid.UUID, db: Session):
    logging.info(f'Fetching order with ID: {order_id}')
    entity = db.query(Order).filter(Order.id == order_id).first()
    if entity:
        logging.info(f'Order found: {entity.id}')
    else:
        logging.warning(f'Order with ID {order_id} not found')
    return entity


def get_all_orders(db: Session):
    logging.info('Fetching all orders.')
    entities = db.query(Order).all()
    logging.info(f'Total orders fetched: {len(entities)}')
    return entities


def delete_order_by_id(order_id: uuid.UUID, db: Session):
    logging.info(f'Deleting order with ID: {order_id}')
    entity = get_order_by_id(order_id, db)
    if entity:
        db.delete(entity)
        db.commit()
        logging.info(f'Order with ID {order_id} deleted successfully.')
    else:
        logging.warning(f'Order with ID {order_id} not found, nothing to delete.')


def update_order_status(order: Order, changed_order: OrderStatus, db: Session):
    logging.info(f'Updating order status for ID: {order.id} to {changed_order}')
    setattr(order, 'order_status', changed_order)
    db.commit()
    db.refresh(order)
    logging.info(f'Order status updated successfully: {order.order_status}')
    return order


def create_pizza(pizza_type: PizzaType, db: Session):
    logging.info(f'Creating a pizza of type: {pizza_type.name if pizza_type else "None"}')
    entity = Pizza()
    if pizza_type:
        entity.pizza_type_id = pizza_type.id
    db.add(entity)
    db.commit()
    logging.info(f'Pizza created successfully with ID: {entity.id}')
    return entity


def add_pizza_to_order(order: Order, pizza_type: PizzaType, db: Session):
    logging.info(f'Adding pizza to order ID: {order.id}')
    pizza = create_pizza(pizza_type, db)
    order.pizzas.append(pizza)
    db.commit()
    db.refresh(order)
    logging.info(f'Pizza added to order ID: {order.id} successfully.')
    return pizza


def get_pizza_by_id(pizza_id: uuid.UUID, db: Session):
    logging.info(f'Fetching pizza with ID: {pizza_id}')
    entity = db.query(Pizza).filter(Pizza.id == pizza_id).first()
    if entity:
        logging.info(f'Pizza found: {entity.id}')
    else:
        logging.warning(f'Pizza with ID {pizza_id} not found')
    return entity


def get_all_pizzas_of_order(order: Order, db: Session):
    logging.info(f'Fetching all pizzas for order ID: {order.id}')
    pizza_types = db.query(Pizza.id, PizzaType.name, PizzaType.price, PizzaType.description, PizzaType.dough_id) \
        .join(Pizza.pizza_type) \
        .filter(Pizza.order_id == order.id)

    returnlist: List[JoinedPizzaPizzaTypeSchema] = []
    for pizza_type in pizza_types.all():
        returnlist.append(pizza_type)

    logging.info(f'Total pizzas fetched for order ID {order.id}: {len(returnlist)}')
    return returnlist


def delete_pizza_from_order(order: Order, pizza_id: uuid.UUID, db: Session):
    logging.info(f'Removing pizza with ID {pizza_id} from order ID: {order.id}')
    entity = db.query(Pizza).filter(Pizza.order_id == order.id, Pizza.id == pizza_id).first()
    if entity:
        db.delete(entity)
        db.commit()
        logging.info(f'Pizza with ID {pizza_id} removed successfully from order ID: {order.id}')
        return True
    else:
        logging.warning(f'Pizza with ID {pizza_id} not found in order ID: {order.id}')
        return False


def create_beverage_quantity(order: Order, schema: OrderBeverageQuantityCreateSchema, db: Session):
    logging.info(f'Adding beverage to order ID: {order.id} with data: {schema.dict()}')
    entity = OrderBeverageQuantity(**schema.dict())
    order.beverages.append(entity)
    db.commit()
    db.refresh(order)
    logging.info(f'Beverage added to order ID: {order.id} successfully.')
    return entity


def get_beverage_quantity_by_id(order_id: uuid.UUID, beverage_id: uuid.UUID, db: Session):
    logging.info(f'Fetching beverage with ID {beverage_id} in order ID {order_id}')
    entity = db.query(OrderBeverageQuantity).filter(
        OrderBeverageQuantity.beverage_id == beverage_id,
        OrderBeverageQuantity.order_id == order_id,
    ).first()
    if entity:
        logging.info(f'Beverage quantity found: {entity.quantity}')
    else:
        logging.warning(f'Beverage with ID {beverage_id} not found in order ID {order_id}')
    return entity


def get_joined_beverage_quantities_by_order(order_id: uuid.UUID, db: Session):
    logging.info(f'Fetching all beverages for order ID: {order_id}')
    entities = db.query(OrderBeverageQuantity).filter(OrderBeverageQuantity.order_id == order_id)
    beverages = entities.all()
    logging.info(f'Total beverages fetched for order ID {order_id}: {len(beverages)}')
    return beverages


def update_beverage_quantity_of_order(order_id: uuid.UUID, beverage_id: uuid.UUID, new_quantity: int, db: Session):
    logging.info(f'Updating beverage quantity for beverage ID {beverage_id} in order ID {order_id} to {new_quantity}')
    order_beverage = db.query(OrderBeverageQuantity).filter(
        order_id == OrderBeverageQuantity.order_id,
        beverage_id == OrderBeverageQuantity.beverage_id,
    ).first()
    if order_beverage:
        setattr(order_beverage, 'quantity', new_quantity)
        db.commit()
        db.refresh(order_beverage)
        logging.info(f'Beverage quantity updated successfully for beverage ID {beverage_id}')
    else:
        logging.warning(f'Beverage with ID {beverage_id} not found in order ID {order_id}')
    return order_beverage


def delete_beverage_from_order(order_id: uuid.UUID, beverage_id: uuid.UUID, db: Session):
    logging.info(f'Removing beverage with ID {beverage_id} from order ID {order_id}')
    entity = db.query(OrderBeverageQuantity).filter(
        order_id == OrderBeverageQuantity.order_id,
        beverage_id == OrderBeverageQuantity.beverage_id,
    ).first()
    if entity:
        db.delete(entity)
        db.commit()
        logging.info(f'Beverage with ID {beverage_id} removed successfully from order ID {order_id}')
        return True
    else:
        logging.warning(f'Beverage with ID {beverage_id} not found in order ID {order_id}')
        return False


def get_price_of_order(order_id: uuid.UUID, db: Session):
    logging.info(f'Calculating total price for order ID: {order_id}')
    price_beverage: float = 0
    for row in db.query(Beverage.price, OrderBeverageQuantity.quantity) \
            .join(OrderBeverageQuantity) \
            .join(Order) \
            .filter(Order.id == order_id):
        price_beverage += (row.price * row.quantity)

    price_pizza = db.query(func.sum(PizzaType.price)) \
        .join(Pizza) \
        .join(Order) \
        .filter(Order.id == order_id).first()[0]

    total_price = price_beverage
    if price_pizza:
        total_price += price_pizza

    logging.info(f'Total price for order ID {order_id}: {total_price}')
    return total_price


def get_orders_by_statuses(statuses: Optional[List[OrderStatus]], db: Session):
    """
    Fetch all orders that match one or more of the given statuses.
    If no statuses are provided, returns all orders.
    """
    logging.info(f'Fetching orders by statuses: {statuses}')
    query = db.query(Order)
    if statuses and len(statuses) > 0:
        query = query.filter(Order.order_status.in_(statuses))
    entities = query.all()
    logging.info(f'Total orders fetched by statuses {statuses or "None"}: {len(entities)}')
    return entities
