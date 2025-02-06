#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from models import db, Restaurant, Pizza, RestaurantPizza

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def home():
    return ""

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([{
        "id": r.id,
        "name": r.name,
        "address": r.address
    } for r in restaurants])

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return make_response(
            jsonify({"error": "Restaurant not found"}),
            404
        )
    return jsonify(restaurant.to_dict())

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return make_response(
            jsonify({"error": "Restaurant not found"}),
            404
        )
    
    db.session.delete(restaurant)
    db.session.commit()
    
    return make_response("", 204)

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([{
        "id": p.id,
        "name": p.name,
        "ingredients": p.ingredients
    } for p in pizzas])

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    try:
        data = request.get_json()
        
        # Check if restaurant and pizza exist
        restaurant = Restaurant.query.get(data.get('restaurant_id'))
        pizza = Pizza.query.get(data.get('pizza_id'))
        
        if not restaurant or not pizza:
            return make_response(
                jsonify({"errors": ["Restaurant/Pizza not found"]}),
                404
            )
        
        # Create new restaurant_pizza
        restaurant_pizza = RestaurantPizza(
            price=data.get('price'),
            pizza_id=data.get('pizza_id'),
            restaurant_id=data.get('restaurant_id')
        )
        
        db.session.add(restaurant_pizza)
        db.session.commit()
        
        return jsonify({
            "id": restaurant_pizza.id,
            "price": restaurant_pizza.price,
            "pizza_id": restaurant_pizza.pizza_id,
            "restaurant_id": restaurant_pizza.restaurant_id,
            "pizza": {
                "id": pizza.id,
                "name": pizza.name,
                "ingredients": pizza.ingredients
            }
        })
        
    except ValueError as e:
        return make_response(
            jsonify({"errors": [str(e)]}),
            400
        )
    except Exception as e:
        return make_response(
            jsonify({"errors": ["validation errors"]}),
            400
        )

if __name__ == '__main__':
    app.run(port=5555, debug=True)