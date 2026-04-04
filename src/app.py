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
from models import db, User, People, Favorite, Nave, Favorite_nave
# from models import serialize
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
def get_users():
    all_user = User.query.all()
    results = list(map(lambda usuario: usuario.serialize() ,all_user))
    
    response_body = {
        "msg": "estos son tus usuarios",
        "users": results
    }

    return jsonify(response_body), 200


@app.route('/person', methods=['GET'])
def get_people():
    all_people = People.query.all()
    personas = list(map(lambda person: person.serialize() ,all_people))
    
    response_body = personas

    return jsonify(personas), 200

@app.route('/nave', methods=['GET'])
def get_nave():
    all_naves = Nave.query.all()
    naves = list(map(lambda nave: nave.serialize() ,all_naves))
    
    response_body = naves

    return jsonify(naves), 200

@app.route('/person/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = db.session.get(People, people_id)

    return jsonify(person.serialize()), 200

# @app.route('/planets', methods=['GET'])
# def get_planets():
#     all_planets = Location.query.all()
#     planets = list(map(lambda planet: planet.serialize() ,all_planets))
    
#     response_body = planets

#     return jsonify(planets), 200

# @app.route('/planets/<int:planet_id>', methods=['GET'])
# def get_planet(planet_id):
#     planet = db.session.get(Location, planet_id)
    
#     return jsonify(planet.serialize()), 200

@app.route('/person', methods=['POST'])
def add_people():
    body = request.get_json()
    if "name" not in body:
        return "Debes enviar un nombre", 400
    if body["name"] == "":
        return {
            "msg":"el nombre no puede estar vacío"
                        }, 400
    person = People(**body)
    db.session.add(person)
    db.session.commit()
 
    all_people = People.query.all()
    personas = list(map(lambda person: person.serialize() ,all_people))
    
    response_body = personas

    return jsonify(personas), 200

@app.route('/person/<int:people_id>', methods=['DELETE'])
def del_person(people_id):
    person = db.session.get(People, people_id)
    if person is None:
        return {
        "msg": "Error eliminado el personaje",
        "msg_error": f"No hay personaje con el identificador #{people_id}",
    }, 400
    
    db.session.delete(person)
    db.session.commit()

    response_body = {
        "msg": "Datos eliminados",
        "personaje":  person.serialize()
    }

    return jsonify(response_body), 200

@app.route('/users/<int:user_id>/favorites/<int:people_id>', methods=['POST'])
def fav_users(user_id, people_id):
    # body = request.get_json()

    person = db.session.get(People, people_id)
    if person is None:
        return {
        "msg": "el persojane no existe",
        "msg_error": f"No hay personaje con el identificador #{people_id}",
    }, 400

    user = db.session.get(User, user_id)
    if user is None:
        return {
        "msg": "Usuario no encontrado",
        "msg_error": f"No hay usuarios con el identificador #{user_id}",
    }, 400


    new_favorite = Favorite(user_id = user_id, people_id = people_id)
    db.session.add(new_favorite)
    db.session.commit()
 
    return jsonify(new_favorite.serialize()), 200

@app.route('/users/<int:user_id>/favorites/nave/<int:nave_id>', methods=['POST'])

def fav_nave(user_id, nave_id):
    # body = request.get_json()

    nave = db.session.get(Nave, nave_id)
    if nave is None:
        return {
        "msg": "La nave no existe",
        "msg_error": f"No hay naves con el identificador #{nave_id}",
    }, 400

    user = db.session.get(User, user_id)
    if user is None:
        return {
        "msg": "Usuario no encontrado",
        "msg_error": f"No hay usuarios con el identificador #{user_id}",
    }, 400


    new_favorite = Favorite_nave(user_id = user_id, nave_id = nave_id)
    db.session.add(new_favorite)
    db.session.commit()
 
    return jsonify(new_favorite.serialize()), 200

@app.route('/users/<int:user_id>/favorites/nave/<int:nave_id>', methods=['DELETE'])
def delete_fav_nave(user_id, nave_id):
    favorite = Favorite_nave.query.filter_by(user_id=user_id, nave_id=nave_id).first()

    if favorite is None:
        return jsonify({
            "msg": "Favorito no encontrado",
            "msg_error": f"No existe esa nave favorita para el usuario #{user_id}"
        }), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({
        "msg": "Nave eliminada de favoritos"
    }), 200

@app.route('/users/<int:user_id>/favorites/<int:people_id>', methods=['DELETE'])
def delete_fav_people(user_id, people_id):
    favorite = Favorite.query.filter_by(user_id=user_id, people_id=people_id).first()

    if favorite is None:
        return jsonify({
            "msg": "Favorito no encontrado",
            "msg_error": f"No existe ese personaje favorito para el usuario #{user_id}"
        }), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({
        "msg": "Personaje eliminado de favoritos"
    }), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)


# para el primero el código es:
# def delete_personaje(personaje_id)
#     variable = Variable.query.filter_by(id = personaje_id).first()