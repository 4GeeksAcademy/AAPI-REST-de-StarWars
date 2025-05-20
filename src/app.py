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
from models import db, User, Profile, People, Planet, Favorite
from sqlalchemy import select
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
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

# **User Methods** ------------------------------------------------->

    # GET Todos los Usuarios
@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

    # GET  Usuario por ID 
@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.serialize()), 200

    # POST  Usuario 
@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Missing or invalid data"}), 400

    existing_user = User.query.filter_by(email=data["email"]).first()
    if existing_user:
        return jsonify({"error": "Email already exists"}), 400

    # En producción, usamos hashing
    new_user = User(email=data["email"], password=data["password"])
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.serialize()), 201

    # PUT  Usuario ID
@app.route("/users/<int:id>", methods=["PUT"])
def update_user(id):
    data = request.get_json()
    user = User.query.get(id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Si no se envía ningún campo para actualizar, devolver error 400
    if not data["email"] and not data["password"]:
        return jsonify({"error": "You must change at least one field"}), 400

    # Si el email ya existe en otro usuario, devolver error 400
    if data.get("email"):
        existing_user = User.query.filter_by(email=data["email"]).first()
        if existing_user and existing_user.id != id:
            return jsonify({"error": "Email is already in use"}), 400

    # Actualizar los campos si se enviaron
    user.email = data.get("email", user.email)
    user.password = data.get("password", user.password)

    db.session.commit()
    return jsonify(user.serialize()), 200

    # DELETE  Usuario ID
@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        # Eliminar favoritos asociados (si es necesario)
        Favorite.query.filter_by(user_id=user_id).delete()

        # Eliminar perfil asociado (si es necesario)
        if user.profile:
            db.session.delete(user.profile)

        # Eliminar el usuario
        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
 #------------------------------------------------->   
     
# **Profiles Methods** ------------------------------------------------->

    # GET Perfiles 
@app.route("/profiles", methods=["GET"])
def get_profiles():
    profiles = Profile.query.all()
    return jsonify([p.serialize() for p in profiles]), 200

    # GET Perfiles ID
@app.route("/profiles/<int:id>", methods=["GET"])
def get_profile(id):
    profile = Profile.query.get(id)
    if not profile:
        return jsonify({"error": "Profile not found"}), 404
    return jsonify(profile.serialize()), 200

    # POST Perfiles ID
@app.route("/profiles/<int:id>", methods=["POST"])
def create_profile(id):
    data = request.get_json()
    if not data or "bio" not in data:
        return jsonify({"error": "Missing data"}), 400

    existing_profile = Profile.query.filter_by(user_id=id).first()
    if existing_profile:
        return jsonify({"error": "Profile already exists"}), 400

    new_profile = Profile(bio=data["bio"], user_id=id)
    db.session.add(new_profile)
    db.session.commit()
    return jsonify(new_profile.serialize()), 201

    # PUT Perfiles ID
@app.route("/profiles/<int:id>", methods=["PUT"])
def update_profile(id):
    profile = Profile.query.get(id)
    if not profile:
        return jsonify({"error": "Profile not found"}), 404

    data = request.get_json()

    # Verificar que al menos un campo se está actualizando
    if not data.get("bio"):
        return jsonify({"error": "You must change at least one field"}), 400

    # Actualizar los valores si se enviaron
    profile.bio = data.get("bio", profile.bio)

    db.session.commit()
    return jsonify(profile.serialize()), 200
  
    # DELETE Perfiles ID
@app.route("/profileseee/<int:user_id>", methods=["DELETE"])
def delete_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Profile not found"}), 404

    try:
        # Eliminar perfil asociado (si es necesario)
        if user.profile:
            db.session.delete(user.profile)
            db.session.commit()

        return jsonify({"message": "Profile deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# **People Methods** ------------------------------------------------->

    # GET People
@app.route('/people', methods=['GET'])
def get_people():
    people_list = People.query.all()
    return jsonify([person.serialize() for person in people_list])

    # GET People ID
@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = People.query.get(people_id)
    if not person:
        return jsonify({"error": "Person not found"}), 404
    return jsonify(person.serialize())

    # POST People 
@app.route("/people/", methods=["POST"])
def create_person():
    data = request.get_json()

    # Validar que los datos sean correctos
    if not data or not data.get("name"):
        return jsonify({"error": "Missing or invalid data"}), 400

    # Verificar si la persona ya existe por nombre
    existing_person = People.query.filter_by(name=data["name"]).first()
    if existing_person:
        return jsonify({"error": "Person already exists"}), 400

    # Crear la nueva persona
    new_person = People(name=data["name"])
    db.session.add(new_person)
    db.session.commit()

    return jsonify(new_person.serialize()), 201

    # PUT People ID
@app.route("/people/<int:id>", methods=["PUT"])
def update_person(id):
    data = request.get_json()
    people = People.query.get(id)
    if not people:
        return jsonify({"error": "People not found"}), 404

    # Si no se envía ningún campo para actualizar, devolver error 400
    if not data.get("name"):
        return jsonify({"error": "You must change at least one field"}), 400

    # Actualizar los campos si se enviaron
    people.name = data.get("name", people.name)

    db.session.commit()
    return jsonify(people.serialize()), 200

    # DELETE People ID
@app.route("/people/<int:people_id>", methods=["DELETE"])
def delete_person(people_id):
    # Verificar si la persona existe
    person = People.query.get(people_id)
    if not person:
        return jsonify({"error": "People not found"}), 404

    try:
        # Eliminar favoritos asociados (si es necesario)
        Favorite.query.filter_by(people_id=people_id).delete()

        # Eliminar la persona
        db.session.delete(person)
        db.session.commit()

        return jsonify({"message": "People deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()  # Revertir cambios en caso de error
        return jsonify({"error": str(e)}), 500

#  ------------------------------------------------->

# **Planets Methods** ------------------------------------------------->

    # GET Todos los Planetas
@app.route('/planets', methods=['GET'])
def get_planets():
    planets_list = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets_list])

    # GET Planetas por ID
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404
    return jsonify(planet.serialize())

    # POST Planetas 
@app.route("/planets", methods=["POST"])
def create_planet():
    data = request.get_json()

    # Validar que los datos sean correctos
    if not data or not data.get("name"):
        return jsonify({"error": "Missing or invalid data"}), 400

    # Verificar si el planeta ya existe por nombre
    existing_planet = Planet.query.filter_by(name=data["name"]).first()
    if existing_planet:
        return jsonify({"error": "Planet already exists"}), 400

    # Crear el nuevo planeta
    new_planet = Planet(name=data["name"])
    db.session.add(new_planet)
    db.session.commit()

    return jsonify(new_planet.serialize()), 201

    # PUT Planetas ID
@app.route("/planet/<int:id>", methods=["PUT"])
def update_planet(id):
    data = request.get_json()
    planet = Planet.query.get(id)
    if not planet:
        return jsonify({"error": "planet not found"}), 404

    # Si no se envía ningún campo para actualizar, devolver error 400
    if not data.get("name"):
        return jsonify({"error": "You must change at least one field"}), 400

    # Actualizar los campos si se enviaron
    planet.name = data.get("name", planet.name)

    db.session.commit()
    return jsonify(planet.serialize()), 200

    # DELETE Planetas ID
@app.route("/planets/<int:planet_id>", methods=["DELETE"])
def delete_planet(planet_id):
    # Verificar si el planeta existe
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404

    try:
        # Eliminar favoritos asociados (si es necesario)
        Favorite.query.filter_by(planet_id=planet_id).delete()

        # Eliminar el planeta
        db.session.delete(planet)
        db.session.commit()

        return jsonify({"message": "Planet deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()  # Revertir cambios en caso de error
        return jsonify({"error": str(e)}), 500
#------------------------------------------------->
    

# **User/s Favorite Methods** ------------------------------------------------->
    # GET Users Favorite
@app.route('/users/favorites', methods=['GET'])
def get_users_with_favorites():
    users = User.query.all()  # ✅ Obtener todos los usuarios

    users_with_favorites = []

    for user in users:
        # ✅ Acceder directamente a los favoritos
        user_favorites = [fav.serialize() for fav in user.favorites]
        if user_favorites:  # ✅ Solo agregar usuarios con favoritos
            users_with_favorites.append({
                "user_id": user.id,
                "email": user.email,
                "favorites": user_favorites
            })

    if not users_with_favorites:
        return jsonify({"message": "No users with favorites found"}), 200

    return jsonify(users_with_favorites)

    # POST Favorite Planet ID 
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add__favorite_planet(planet_id):
    data = request.get_json()
    user_id = data.get("user_id")  # obtener el usuario seleccionado

    # verificacion de si el usuario existe en bd

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "The selected user does not exist in the database"}), 404

    # verificacion del planeta a asignar como favorito existe en bd

    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "The selected planet does not exist in the database."})

    # verificacion de si el favorito ya existe en el usuario a añadir

    existing_favorite = Favorite.query.filter_by(
        user_id=user_id, planet_id=planet_id).first()
    if existing_favorite:
        return jsonify({"error": "The favorite to add in user_id is already a favorite"}), 400

    # creacion del nuevo favorito

    new_favorite = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({"message": "Favorite planet added successfully"}), 201

    # POST Favorite People  ID
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_person(people_id):
    data = request.get_json()
    user_id = data.get("user_id")  # Obtener el usuario seleccionado

    # Verificación de si el usuario existe en la BD
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "The selected user does not exist in the database."}), 404

    # Verificación de si la persona a asignar como favorita existe en la BD
    person = People.query.get(people_id)
    if not person:
        return jsonify({"error": "The selected person does not exist in the database."}), 404

    # Verificación de si el favorito ya existe en el usuario
    existing_favorite = Favorite.query.filter_by(
        user_id=user_id, people_id=people_id).first()
    if existing_favorite:
        return jsonify({"error": "The person is already a favorite"}), 400

    # Creación del nuevo favorito
    new_favorite = Favorite(user_id=user_id, people_id=people_id)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({"message": "Favorite people added successfully"}), 201


    # DELETE Favorite Planet ID
@app.route("/favorite/planet/<int:planet_id>", methods=["DELETE"])
def delete_favorite_planet(planet_id):
    # Verificar si el favorito existe
    favorite = Favorite.query.filter_by(planet_id=planet_id).first()
    if not favorite:
        return jsonify({"error": "Favorite planet not found"}), 404

    try:
        # Eliminar el favorito
        db.session.delete(favorite)
        db.session.commit()

        return jsonify({"message": "Favorite planet deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()  # Revertir cambios en caso de error
        return jsonify({"error": str(e)}), 500

    # DELETE Favorite People ID
@app.route("/favorite/people/<int:people_id>", methods=["DELETE"])
def delete_favorite_people(people_id):
    # Verificar si el favorito existe
    favorite = Favorite.query.filter_by(people_id=people_id).first()
    if not favorite:
        return jsonify({"error": "Favorite people not found"}), 404

    try:
        # Eliminar el favorito
        db.session.delete(favorite)
        db.session.commit()

        return jsonify({"message": "Favorite people deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()  # Revertir cambios en caso de error
        return jsonify({"error": str(e)}), 500
