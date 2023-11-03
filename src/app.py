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
from models import db, User, People, Planets, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
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
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


@app.route ('/people', methods=['GET'])
def get_people():
    people = People()
    people = people.query.all()
    return jsonify(list(map(lambda item : item.serialize(), people))), 200

@app.route ('/people/<int:theid>', methods=['GET'])
def get_character(theid=None):
    if theid is None:
        return ({"message": "the id is necessary"}), 404
    character = People()
    character = character.query.get(theid)
    if character is None:
        return ({"message": "character doesn't exist"})
    return jsonify((character.serialize())), 200

@app.route ('/planets', methods=['GET'])
def get_planets():
    planets = Planets()
    planets = planets.query.all()
    return jsonify(list(map(lambda item : item.serialize(), planets))), 200

@app.route ('/planets/<int:theid>', methods=['GET'])
def get_planet(theid=None):
    if theid is None:
        return ({"message": "the id is necessary"}), 404
    planet = Planets()
    planet = planet.query.get(theid)
    if planet is None:
        return ({"message": "planet doesn't exist"})
    return jsonify((planet.serialize())), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
