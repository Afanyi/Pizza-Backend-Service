import logging
import uuid
from typing import List, Optional, TypeVar

from fastapi import APIRouter, Depends, Request, Response, status, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

import app.api.v1.endpoints.beverage.crud as beverage_crud
import app.api.v1.endpoints.order.crud as order_crud
import app.api.v1.endpoints.order.stock_logic.stock_beverage_crud as stock_beverage_crud
import app.api.v1.endpoints.order.stock_logic.stock_ingredients_crud as stock_ingredients_crud
import app.api.v1.endpoints.pizza_type.crud as pizza_type_crud
import app.api.v1.endpoints.user.crud as user_crud
from app.api.v1.endpoints.order.schemas \
    import OrderSchema, PizzaCreateSchema, JoinedPizzaPizzaTypeSchema, \
    PizzaWithoutPizzaTypeSchema, OrderBeverageQuantityCreateSchema, JoinedOrderBeverageQuantitySchema, \
    OrderPriceSchema, OrderBeverageQuantityBaseSchema, OrderCreateSchema, OrderStatus
from app.api.v1.endpoints.user.schemas import UserSchema
from app.database.connection import SessionLocal

ITEM_NOT_FOUND = 'Item not found'

# Configure logger
logging.basicConfig(level=logging.INFO)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get('/statuses', response_model=List[OrderSchema], tags=['order'])
def get_orders_by_status(
    statuses: Optional[List[str]] = Query(None, description='Filter orders by one or more statuses'),
    db: Session = Depends(get_db),
):
    """
    Fetch all orders that match one or more of the given statuses.
    If no statuses are provided, returns all orders.
    """
    logging.info(f'Fetching orders with statuses: {statuses}')
    if statuses:
        # Convert string statuses to OrderStatus Enum
        try:
            status_enums = [OrderStatus[status.upper()] for status in statuses]
        except KeyError as e:
            logging.warning(f'Invalid status provided: {e}')
            raise HTTPException(
                status_code=400, detail=f'Invalid order status: {e}',
            )
    else:
        status_enums = None  # If no statuses are provided, fetch all orders

    # Fetch orders using the CRUD function
    orders = order_crud.get_orders_by_statuses(status_enums, db)
    logging.info(f'Total orders fetched with statuses {statuses}: {len(orders)}')
    return orders


@router.put('/{order_id}', status_code=204, tags=['order'])
def update_order_status(
    order_id: uuid.UUID,
    order_status: str,
    db: Session = Depends(get_db),
):
    """
    Update the status of an order by ID.
    """
    logging.info(f'Updating order status for ID: {order_id} to {order_status}')

    # Fetch the order
    order = order_crud.get_order_by_id(order_id, db)
    if not order:
        logging.warning(f'Order with ID {order_id} not found.')
        raise HTTPException(status_code=404, detail='Order not found')

    # Validate the provided status
    try:
        new_status = OrderStatus[order_status.upper()]
    except KeyError:
        logging.warning(f'Invalid order status provided: {order_status}')
        raise HTTPException(status_code=422, detail='Invalid order status')

    # Update the order status
    order_crud.update_order_status(order, new_status, db)
    logging.info(f'Order status updated successfully for ID {order_id} to {new_status}')
    return Response(status_code=204)


@router.get('', response_model=List[OrderSchema], tags=['order'])
def get_all_orders(db: Session = Depends(get_db)):
    logging.info('Fetching all orders.')
    orders = order_crud.get_all_orders(db)
    logging.info(f'Total orders fetched: {len(orders)}')
    return orders


@router.post('', response_model=OrderSchema, status_code=status.HTTP_201_CREATED, tags=['order'])
def create_order(order: OrderCreateSchema, db: Session = Depends(get_db), copy_order_id: Optional[uuid.UUID] = None):
    logging.info(f'Creating a new order for user_id: {order.user_id}')
    if user_crud.get_user_by_id(order.user_id, db) is None:
        logging.warning(f'User with ID {order.user_id} not found.')
        raise HTTPException(status_code=404, detail=ITEM_NOT_FOUND)

    new_order = order_crud.create_order(order, db)
    logging.info(f'Order created successfully with ID: {new_order.id}')

    if copy_order_id is None:
        return new_order

    logging.info(f'Copying items from order ID: {copy_order_id}')
    copy_order = order_crud.get_order_by_id(copy_order_id, db)
    if not copy_order:
        logging.warning(f'Copy order with ID {copy_order_id} not found.')
        order_crud.delete_order_by_id(new_order.id, db)
        raise HTTPException(status_code=404, detail=ITEM_NOT_FOUND)

    for pizza in copy_order.pizzas:
        pizza_type = pizza.pizza_type
        if not stock_ingredients_crud.ingredients_are_available(pizza_type):
            logging.warning(f'Insufficient stock for pizza type: {pizza_type.name}')
            order_crud.delete_order_by_id(new_order.id, db)
            raise HTTPException(status_code=409, detail='Conflict')
        order_crud.add_pizza_to_order(new_order, pizza_type, db)
        stock_ingredients_crud.reduce_stock_of_ingredients(pizza_type, db)

    for beverage_quantity in copy_order.beverages:
        schema = OrderBeverageQuantityCreateSchema(
            quantity=beverage_quantity.quantity, beverage_id=beverage_quantity.beverage_id)
        if not stock_beverage_crud.change_stock_of_beverage(beverage_quantity.beverage_id,
                                                            -beverage_quantity.quantity, db):
            logging.warning(f'Insufficient stock for beverage ID: {beverage_quantity.beverage_id}')
            order_crud.delete_order_by_id(new_order.id, db)
            raise HTTPException(status_code=409, detail='Conflict')
        order_crud.create_beverage_quantity(new_order, schema, db)

    logging.info(f'Items copied successfully to new order ID: {new_order.id}')
    return new_order


@router.get('/{order_id}', response_model=OrderSchema, tags=['order'])
def get_order(order_id: uuid.UUID, db: Session = Depends(get_db)):
    logging.info(f'Fetching order with ID: {order_id}')
    order = order_crud.get_order_by_id(order_id, db)
    if not order:
        logging.warning(f'Order with ID {order_id} not found.')
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    logging.info(f'Order fetched successfully: {order.id}')
    return order


@router.delete('/{order_id}', response_model=None, tags=['order'])
def delete_order(order_id: uuid.UUID, db: Session = Depends(get_db)):
    logging.info(f'Deleting order with ID: {order_id}')
    order = order_crud.get_order_by_id(order_id, db)
    if not order:
        logging.warning(f'Order with ID {order_id} not found.')
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    logging.info(f'Restoring stock for items in order ID: {order_id}')
    for pizza in order.pizzas:
        stock_ingredients_crud.increase_stock_of_ingredients(pizza.pizza_type, db)

    for beverage in order.beverages:
        stock_beverage_crud.change_stock_of_beverage(beverage.beverage_id, beverage.quantity, db)

    order_crud.delete_order_by_id(order_id, db)
    logging.info(f'Order with ID {order_id} deleted successfully.')
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post('/{order_id}/pizzas', response_model=PizzaWithoutPizzaTypeSchema, tags=['order'])
def add_pizza_to_order(order_id: uuid.UUID, schema: PizzaCreateSchema, db: Session = Depends(get_db)):
    logging.info(f'Adding pizza to order ID: {order_id}')
    order = order_crud.get_order_by_id(order_id, db)
    if not order:
        logging.warning(f'Order with ID {order_id} not found.')
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    pizza_type = pizza_type_crud.get_pizza_type_by_id(schema.pizza_type_id, db)
    if not pizza_type:
        logging.warning(f'Pizza type with ID {schema.pizza_type_id} not found.')
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    if not stock_ingredients_crud.ingredients_are_available(pizza_type):
        logging.warning(f'Insufficient stock for pizza type ID {pizza_type.id}')
        return Response(status_code=status.HTTP_409_CONFLICT)

    stock_ingredients_crud.reduce_stock_of_ingredients(pizza_type, db)
    pizza = order_crud.add_pizza_to_order(order, pizza_type, db)
    logging.info(f'Pizza added successfully to order ID: {order_id}')
    return pizza


@router.get('/{order_id}/pizzas', response_model=List[JoinedPizzaPizzaTypeSchema], tags=['order'])
def get_pizzas_from_order(order_id: uuid.UUID, db: Session = Depends(get_db)):
    logging.info(f'Fetching pizzas from order ID: {order_id}')
    order = order_crud.get_order_by_id(order_id, db)
    if not order:
        logging.warning(f'Order with ID {order_id} not found.')
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    pizzas = order_crud.get_all_pizzas_of_order(order, db)
    logging.info(f'Pizzas fetched successfully from order ID: {order_id}')
    return pizzas


@router.delete('/{order_id}/pizzas', response_model=None, tags=['order'])
def delete_pizza_from_order(order_id: uuid.UUID, pizza: PizzaWithoutPizzaTypeSchema, db: Session = Depends(get_db)):
    logging.info(f'Deleting pizza with ID {pizza.id} from order ID: {order_id}')
    order = order_crud.get_order_by_id(order_id, db)
    if not order:
        logging.warning(f'Order with ID {order_id} not found.')
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    pizza_entity = order_crud.get_pizza_by_id(pizza.id, db)
    if not pizza_entity:
        logging.warning(f'Pizza with ID {pizza.id} not found.')
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    stock_ingredients_crud.increase_stock_of_ingredients(pizza_entity.pizza_type, db)
    if not order_crud.delete_pizza_from_order(order, pizza.id, db):
        logging.warning(f'Failed to delete pizza with ID {pizza.id} from order ID: {order_id}')
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    logging.info(f'Pizza with ID {pizza.id} deleted successfully from order ID: {order_id}')
    return Response(status_code=status.HTTP_200_OK)


MyPyEitherItem = TypeVar(
    'MyPyEitherItem',
    List[OrderBeverageQuantityCreateSchema],
    List[JoinedOrderBeverageQuantitySchema],
    None,
)


@router.get('/{order_id}/beverages', response_model=MyPyEitherItem, tags=['order'])
def get_order_beverages(order_id: uuid.UUID, db: Session = Depends(get_db), join: bool = False):
    logging.info(f'Fetching beverages from order ID: {order_id}')
    order = order_crud.get_order_by_id(order_id, db)
    if not order:
        logging.warning(f'Order with ID {order_id} not found.')
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    beverages = order.beverages
    if join:
        beverages = order_crud.get_joined_beverage_quantities_by_order(order.id, db)

    logging.info(f'Beverages fetched successfully from order ID: {order_id}')
    return beverages


@router.post('/{order_id}/beverages', response_model=OrderBeverageQuantityCreateSchema,
             status_code=status.HTTP_201_CREATED, tags=['order'])
def create_order_beverage(order_id: uuid.UUID, beverage_quantity: OrderBeverageQuantityCreateSchema,
                          request: Request, db: Session = Depends(get_db)):
    logging.info(f'Adding beverage to order ID: {order_id}')
    order = order_crud.get_order_by_id(order_id, db)
    if not order:
        logging.warning(f'Order with ID {order_id} not found.')
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    if beverage_quantity.quantity <= 0:
        logging.warning(f'Invalid beverage quantity: {beverage_quantity.quantity}')
        raise HTTPException(status_code=422)

    beverage = beverage_crud.get_beverage_by_id(beverage_quantity.beverage_id, db)
    if not beverage:
        logging.warning(f'Beverage with ID {beverage_quantity.beverage_id} not found.')
        raise HTTPException(status_code=404, detail=ITEM_NOT_FOUND)

    beverage_quantity_found = order_crud.get_beverage_quantity_by_id(order_id, beverage_quantity.beverage_id, db)
    if beverage_quantity_found:
        url = request.url_for('get_order_beverages', order_id=beverage_quantity_found.order_id)
        return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

    if not stock_beverage_crud.beverage_is_available(beverage_quantity.beverage_id, beverage_quantity.quantity, db):
        logging.warning(f'Insufficient stock for beverage ID {beverage_quantity.beverage_id}')
        raise HTTPException(status_code=409, detail='Conflict')

    stock_beverage_crud.change_stock_of_beverage(beverage_quantity.beverage_id, -beverage_quantity.quantity, db)
    new_beverage_quantity = order_crud.create_beverage_quantity(order, beverage_quantity, db)
    logging.info(f'Beverage added successfully to order ID: {order_id}')
    return new_beverage_quantity


@router.put('/{order_id}/beverages', response_model=OrderBeverageQuantityBaseSchema, tags=['order'])
def update_beverage_of_order(order_id: uuid.UUID, beverage_quantity: OrderBeverageQuantityCreateSchema,
                             db: Session = Depends(get_db)):
    logging.info(f'Updating beverage in order ID: {order_id}')
    order = order_crud.get_order_by_id(order_id, db)
    if not order:
        logging.warning(f'Order with ID {order_id} not found.')
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    if beverage_quantity.quantity <= 0:
        logging.warning(f'Invalid beverage quantity: {beverage_quantity.quantity}')
        return Response(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    beverage_id = beverage_quantity.beverage_id
    order_beverage_quantity = order_crud.get_beverage_quantity_by_id(order_id, beverage_id, db)
    if not order_beverage_quantity:
        logging.warning(f'Beverage with ID {beverage_id} not found in order ID {order_id}')
        raise HTTPException(status_code=404, detail=ITEM_NOT_FOUND)

    new_quantity = beverage_quantity.quantity
    old_quantity = order_beverage_quantity.quantity

    if not stock_beverage_crud.change_stock_of_beverage(beverage_id, old_quantity - new_quantity, db):
        logging.warning(f'Insufficient stock for beverage ID {beverage_id}')
        raise HTTPException(status_code=409, detail='Conflict')

    updated_beverage_quantity = order_crud.update_beverage_quantity_of_order(order_id, beverage_id, new_quantity, db)
    logging.info(f'Beverage with ID {beverage_id} updated successfully in order ID: {order_id}')
    return updated_beverage_quantity


@router.delete('/{order_id}/beverages', response_model=None, tags=['order'])
def delete_beverage_from_order(order_id: uuid.UUID, beverage_id: uuid.UUID, db: Session = Depends(get_db)):
    logging.info(f'Deleting beverage with ID {beverage_id} from order ID: {order_id}')
    order = order_crud.get_order_by_id(order_id, db)
    if not order:
        logging.warning(f'Order with ID {order_id} not found.')
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    order_beverage = order_crud.get_beverage_quantity_by_id(order_id, beverage_id, db)
    if not order_beverage:
        logging.warning(f'Beverage with ID {beverage_id} not found in order ID {order_id}')
        raise HTTPException(status_code=404, detail=ITEM_NOT_FOUND)

    stock_beverage_crud.change_stock_of_beverage(beverage_id, order_beverage.quantity, db)
    order_crud.delete_beverage_from_order(order_id, beverage_id, db)
    logging.info(f'Beverage with ID {beverage_id} deleted successfully from order ID: {order_id}')
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get('/{order_id}/price', status_code=status.HTTP_200_OK, response_model=OrderPriceSchema, tags=['order'])
def get_price_of_order(order_id: uuid.UUID, db: Session = Depends(get_db)):
    logging.info(f'Calculating total price for order ID: {order_id}')
    order = order_crud.get_order_by_id(order_id, db)
    if not order:
        logging.warning(f'Order with ID {order_id} not found.')
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    price = order_crud.get_price_of_order(order_id, db)
    logging.info(f'Total price for order ID {order_id}: {price}')
    return OrderPriceSchema(price=price)


@router.get('/{order_id}/user', status_code=status.HTTP_200_OK, response_model=UserSchema, tags=['order'])
def get_user_of_order(order_id: uuid.UUID, db: Session = Depends(get_db)):
    logging.info(f'Fetching user for order ID: {order_id}')
    order = order_crud.get_order_by_id(order_id, db)
    if not order:
        logging.warning(f'Order with ID {order_id} not found.')
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    user = order.user
    logging.info(f'User fetched successfully for order ID: {order_id}')
    return user
