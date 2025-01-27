#!/usr/bin/env python3
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
from flask_migrate import Migrate

from models import db, Restaurant, RestaurantPizza, Pizza

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


# ---------- RESTful Resource Classes ---------- #

class RestaurantsResource(Resource):
    def get(self):
        """GET /restaurants"""
        restaurants = Restaurant.query.all()
        # Return only id, name, address (no restaurant_pizzas).
        return [r.to_dict(only=("id", "name", "address")) for r in restaurants], 200


class RestaurantByIDResource(Resource):
    def get(self, id):
        """GET /restaurants/<int:id>"""
        restaurant = db.session.get(Restaurant, id)
        if not restaurant:
            return {"error": "Restaurant not found"}, 404

        # Return full detail, including restaurant_pizzas + nested pizza
        return restaurant.to_dict(), 200

    def delete(self, id):
        """DELETE /restaurants/<int:id>"""
        restaurant = db.session.get(Restaurant, id)
        if not restaurant:
            return {"error": "Restaurant not found"}, 404

        db.session.delete(restaurant)  # cascades to restaurant_pizzas
        db.session.commit()

        return "", 204


class PizzasResource(Resource):
    def get(self):
        """GET /pizzas"""
        pizzas = Pizza.query.all()
        # Return only id, name, ingredients (no restaurant_pizzas).
        return [p.to_dict(only=("id", "name", "ingredients")) for p in pizzas], 200


class RestaurantPizzasResource(Resource):
    def post(self):
        """POST /restaurant_pizzas"""
        data = request.get_json()
        try:
            new_rp = RestaurantPizza(
                price=data["price"],
                pizza_id=data["pizza_id"],
                restaurant_id=data["restaurant_id"]
            )
            db.session.add(new_rp)
            db.session.commit()
        except ValueError:
            # The validation fails if price < 1 or > 30 => raise ValueError
            return {"errors": ["validation errors"]}, 400
        except KeyError:
            # If the JSON is missing something (not tested, but just in case)
            return {"errors": ["missing fields"]}, 400

        # If created OK, return 201 with the new RestaurantPizza data
        return new_rp.to_dict(), 201


# ---------- Assign Resources to Routes ---------- #
api.add_resource(RestaurantsResource, "/restaurants")
api.add_resource(RestaurantByIDResource, "/restaurants/<int:id>")
api.add_resource(PizzasResource, "/pizzas")
api.add_resource(RestaurantPizzasResource, "/restaurant_pizzas")


if __name__ == "__main__":
    app.run(port=5555, debug=True)