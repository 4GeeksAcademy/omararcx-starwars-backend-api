from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    id=db.Column(db.Integer(), primary_key=True)
    username= db.Column(db.String(30), nullable=False, unique=True)
    name = db.Column(db.String(80), nullable=False)
    lastname= db.Column(db.String(80), nullable=False)
    age=db.Column(db.Integer(), nullable=True)
    email=db.Column(db.String(80), nullable=True, unique=True)
    country=db.Column(db.String(60), nullable=True)
    favorites = db.relationship("Favorite", uselist=True, backref='user')

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "lastname": self.lastname,
            "age": self.age,
            "email": self.email,
            "country": self.country,
            "favorites": list(map(lambda item: item.serialize(), self.favorites))
        }
      


class People(db.Model):
    id= db.Column(db.Integer(), primary_key=True)
    name= db.Column(db.String(80), nullable=False)
    side= db.Column(db.String(30), nullable=True)
    status= db.Column(db.String(30), nullable=True)
    origin= db.Column(db.String(30), nullable=True)
    favorites= db.relationship("Favorite", backref='people')

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "side": self.side,
            "status": self.status, 
            "origin": self.origin,
        }

class Planets(db.Model):
    id=db.Column(db.Integer(), primary_key=True, nullable=False)
    name=db.Column(db.String(150), nullable=False)
    population=db.Column(db.Integer(), nullable=True)
    controled=db.Column(db.String(150), nullable=True)
    terrain = db.Column(db.String(120), nullable=False)
    favorites=db.relationship("Favorite", backref="planets")

    def serialize(self):
            return {
                "id": self.id,
                "name": self.name,
                "population": self.population, 
                "controles": self.controled,
                "terrain" : self.terrain
            }
        

class Favorite(db.Model):
    id=db.Column(db.Integer(), primary_key=True)
    user_id=db.Column(db.Integer(),db.ForeignKey("user.id"))
    planet_id=db.Column(db.Integer(),db.ForeignKey("planets.id"))
    people_id=db.Column(db.Integer(),db.ForeignKey("people.id"))

    def serialize(self):
            return {
                "id": self.id,
                "user_id": self.user_id,
                "people_id": self.people_id,
                "planet_id": self.planet_id,
            # do not serialize the password, its a security breach

        }