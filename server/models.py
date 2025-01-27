
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)

class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # Relationships
    restaurant_pizzas = db.relationship(
        "RestaurantPizza",
        backref="restaurant",
        cascade="all, delete-orphan"
    )

    # We won't directly relate Pizza <-> Restaurant except through RestaurantPizza,
    # but you could use association_proxy if you want:
    # pizzas = association_proxy("restaurant_pizzas", "pizza")

    # Serialization rules:
    #  - Exclude the reverse reference from each restaurant_pizza => restaurant
    #    to avoid infinite recursion.
    serialize_rules = (
        "-restaurant_pizzas.restaurant",
    )

    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # Relationships
    restaurant_pizzas = db.relationship("RestaurantPizza", backref="pizza")

    # Optionally:
    # restaurants = association_proxy("restaurant_pizzas", "restaurant")

    # Exclude the reverse reference from each restaurant_pizza => pizza
    # to avoid infinite recursion:
    serialize_rules = (
        "-restaurant_pizzas.pizza",
    )

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"))
    pizza_id = db.Column(db.Integer, db.ForeignKey("pizzas.id"))

    # By default, each RestaurantPizza .to_dict() will include associated
    # `pizza` and `restaurant` unless we exclude them.
    # We do *not* want to create infinite recursion or redundancy, so we can limit it:
    serialize_rules = (
        "-pizza.restaurant_pizzas",
        "-restaurant.restaurant_pizzas",
    )

    @validates("price")
    def validate_price(self, key, value):
        if value < 1 or value > 30:
            # The tests expect a ValueError to be raised
            raise ValueError("Price must be between 1 and 30")
        return value

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"