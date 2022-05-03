"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planets
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_all_users():

    users = User.query.all()
    users_list = list(map(lambda x: x.serialize(), users))

    return jsonify(users_list), 200


@app.route('/user/<int:user_id>', methods=['GET'])
def handle_each_user(user_id):

    user = User.query.get(user_id)
    return jsonify(user.serialize())


@app.route('/user', methods=['POST'])
def create_user():
    request_body = request.get_json()
    new_user = User(email=request_body['email'], password=request_body['password'])
    db.session.add(new_user)
    db.session.commit()
    return f"A new user {request_body['email']} was successfully added", 200


@app.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):

    request_body = request.get_json()
    user = User.query.get(user_id)
    if user is None:
        raise APIException('User not found', status_code=404)

    if "email" in request_body:
        user.email = request_body["email"]
    if "password" in request_body:
        user.password = request_body["password"]
    db.session.commit()
    return jsonify(user.serialize())


@app.route('/planets', methods=['GET'])
def handle_planets():
    planets = Planets.query.all()
    planets_list = list(map(lambda x : x.serialize(), planets))
    
    return jsonify(planets_list), 200



# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
