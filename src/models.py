from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    
    profile = db.relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    favorites = db.relationship("Favorite", back_populates="user_fav", cascade="all, delete-orphan")  # ✅ Relación con favoritos

    def serialize(self):
        data = {
            "id": self.id,
            "email": self.email,
        }

        # Agregar profile solo si existe
        if self.profile:
            data["profile"] = self.profile.serialize()

        # Filtrar favoritos y agregar solo si hay datos
        favorite_people = [fav.people.serialize() for fav in self.favorites if fav.people]
        favorite_planets = [fav.planet.serialize() for fav in self.favorites if fav.planet]

        if favorite_people or favorite_planets:
            data["favorites"] = {
                "people": favorite_people,
                "planets": favorite_planets
            }

        return data
    
class Profile(db.Model):
    __tablename__ = "profiles"
    id = db.Column(db.Integer, primary_key=True)
    bio = db.Column(db.String(250))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = db.relationship("User", back_populates="profile")

    def serialize(self):
        data = {"id": self.id}

        # Agregar bio solo si tiene contenido
        if self.bio:
            data["bio"] = self.bio

        return data

class People(db.Model):
    __tablename__ = "people"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="people")  # ✅ Relación inversa

    def serialize(self):
        return {"id": self.id, "name": self.name}

class Planet(db.Model):
    __tablename__ = "planets"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="planet")  # ✅ Relación inversa

    def serialize(self):
        return {"id": self.id, "name": self.name}
    

    

class Favorite(db.Model):
    __tablename__ = "favorites"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    people_id = db.Column(db.Integer, db.ForeignKey("people.id"), nullable=True)
    planet_id = db.Column(db.Integer, db.ForeignKey("planets.id"), nullable=True)



    user_fav = db.relationship("User", back_populates="favorites")
    people = db.relationship("People", back_populates="favorites")  # ✅ Relación con People
    planet = db.relationship("Planet", back_populates="favorites")  # ✅ Relación con Planet


    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "people": self.people.serialize() if self.people else None,  # ✅ Solo si existe
            "planet": self.planet.serialize() if self.planet else None   # 
        }