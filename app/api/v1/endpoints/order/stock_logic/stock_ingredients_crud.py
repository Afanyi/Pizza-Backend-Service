from sqlalchemy.orm import Session
import logging

from app.database.models import PizzaType


def ingredients_are_available(pizza_type: PizzaType):
    if pizza_type.dough.stock == 0:
        logging.warning(f' stock for dough is zero {pizza_type.dough.name}')
        return False

    for topping_quantity in pizza_type.toppings:
        if topping_quantity.topping.stock < topping_quantity.quantity:
            logging.warning(f' not enough topping with name  {topping_quantity.topping.name}')
            return False

    return True


def reduce_stock_of_ingredients(pizza_type: PizzaType, db: Session):
    pizza_type.dough.stock -= 1
    for topping_quantity in pizza_type.toppings:
        topping_quantity.topping.stock -= topping_quantity.quantity

    db.commit()


def increase_stock_of_ingredients(pizza_type: PizzaType, db: Session):
    pizza_type.dough.stock += 1

    for topping_quantity in pizza_type.toppings:
        topping_quantity.topping.stock += topping_quantity.quantity

    db.commit()
