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

@app.route ('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify(list(map(lambda item : item.serialize(), users))), 200

@app.route ('/users/favorites/<int:theid>', methods=['GET'])
def get_user_favorites(theid=None):
    user_favorites = Favorite.query.filter_by(user_id=theid)
    
    return jsonify(list(map(lambda user_favorites: user_favorites.serialize(), user_favorites))), 200


#[POST] /favorite/planet/<int:planet_id> Add a new favorite planet to the current user with the planet id = planet_id.

@app.route ('/favorite/<string:nature>/<int:planetid>/<int:theid>', methods = ['POST']) 
def add_planet(nature, planetid, theid):
    if nature.lower() == "planet":
        favorite = Favorite.query.filter_by(user_id=theid, planet_id=planetid).first()

        if favorite:
            return ({"message": "planet already exists in favorites"}), 400

        new_planet = Favorite(planet_id=planetid, user_id=theid)

        db.session.add(new_planet)
        
        try:
            db.session.commit()
            return jsonify({"message": "planet added to favorites"}), 200
        except Exception as error:
            db.session.rollback()
            return jsonify({"message": "error"}), 500 

    if nature.lower() == "people":
        favorite = Favorite.query.filter_by(user_id=theid, people_id=planetid).first()

        if favorite:
            return ({"message": "character already exists in favorites"}), 400

        new_character = Favorite(people_id=planetid, user_id=theid)

        db.session.add(new_character)
        
        try:
            db.session.commit()
            return jsonify({"message": "character added to favorites"}), 200
        except Exception as error:
            db.session.rollback()
            return jsonify({"message": "error"}), 500 


@app.route('/favorite/<string:nature>/<int:favoriteid>/<int:theid>', methods=['DELETE'])
def delete_favorite(nature, favoriteid, theid):
    if nature.lower()== 'planet':
        favorite_planet = Favorite.query.filter_by(user_id=theid, planet_id=favoriteid).first()
      
        if favorite_planet is None:
            return ({"message": "Planet is not in this user favorites"}), 400
       
        db.session.delete(favorite_planet)

        try:
            db.session.commit()
            return jsonify({"message": "Planet erased succesfully"}), 200
        except Exception as error:
            db.session.rollback()
            return jsonify({"message": "error"}), 500
        
    if nature.lower()== 'people':
        favorite_character = Favorite.query.filter_by(user_id=theid, people_id=favoriteid).first()

        if favorite_character is None:
            return ({"message": "Character is not in this user favorites"}), 400
      
        db.session.delete(favorite_character)
        try:
            db.session.commit()
            return jsonify({"message": "Character erased succesfully"}), 200
        except Exception as error:
            db.session.rollback()
            return jsonify({"message": "error"}), 500

# Endpoint para modificar character

@app.route ('/people/<int:theid>', methods = ['PUT'])
def update_character(theid):
    if theid is None:
        return ({"message": "the id is necessary"}), 404
    body= request.json
    if body.get("name") is None:
        return jsonify({"message":"name needed"}), 404
    character = People.query.get(theid)
    if character is None:
        return jsonify({"message":"character doesn't exist"}), 404
    character.name= body.get("name")

    try:
        db.session.commit()
        return jsonify({"message":"Character modified"})

    except Exception as error:
        db.session.rollback()
        return jsonify({"message": "error"}), 500
    
@app.route ('/planet/<int:theid>', methods = ['PUT'])
def update_planet(theid):
    if theid is None:
        return ({"message": "the id is necessary"}), 404
    body= request.json
    if body.get("name") is None:
        return jsonify({"message":"name needed"}), 404
    planet = Planets.query.get(theid)
    if planet is None:
        return jsonify({"message":"character doesn't exist"}), 404
    planet.name= body.get("name")
    planet.population = body.get("population")

    try:
        db.session.commit()
        return jsonify({"message":"Planet modified"})

    except Exception as error:
        db.session.rollback()
        return jsonify({"message": "error"}), 500
    
# Endpoint para un nuevo character
@app.route('/people', methods= ['POST'])
def add_character():
    body = request.json
    if body.get("name") is None:
        return ({"message": "A name is necessary"}), 404 
    character = People(name=body.get("name"), side =body.get("side"), status = body.get("status"))
    db.session.add(character)
    try:
        db.session.commit()
        return jsonify({"message":"Character added"})

    except Exception as error:
        db.session.rollback()
        return jsonify({"message": "error"}), 500

#Endpoint para crear un nuevo planeta
@app.route('/planet', methods= ['POST'])
def add__new_planet():
    body = request.json
    if body.get("name") is None:
        return ({"message": "A name is necessary"}), 404 
    planet = Planets(name=body.get("name"), population =body.get("population"), terrain = body.get("terrain"))
    db.session.add(planet)
    try:
        db.session.commit()
        return jsonify({"message":"Planet added"}), 200

    except Exception as error:
        db.session.rollback()
        return jsonify({"message": "error"}), 500

#Endpoint para borrar planeta 
@app.route('/planet/<int:planetid>', methods=['DELETE'])
def delete_planet(planetid):
    planet = Planets.query.get(planetid) 
    if planet is None:
       return jsonify({"message":"Planet doesn't exist"}), 404
    db.session.delete(planet)
    try:
        db.session.commit()
        return jsonify({"message":"Planet erased"}), 200
    except Exception as error:
        db.session.rollback()
        return jsonify({"message": "error"}), 500


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
