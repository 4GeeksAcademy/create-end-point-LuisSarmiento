from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    
    favorite: Mapped[list["Favorite"]] = relationship(
        "Favorite", 
        back_populates = "user"
    )

    favorite_nave: Mapped[list["Favorite_nave"]] = relationship(
        "Favorite_nave", 
        back_populates = "user"
    )


    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "favoritos": [fav.serialize() for fav in self.favorite],
            "nave_favorita": [fav.serialize() for fav in self.favorite_nave]
    }

class People(db.Model):
    __tablename__ = "people"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    
    favorited_by: Mapped[list["Favorite"]] = relationship(
        "Favorite", 
        back_populates = "person"
    )

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
        }

class Favorite(db.Model):
    __tablename__ = "favorite"
    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    people_id: Mapped[int] = mapped_column(ForeignKey("people.id"), nullable=False)
    
    user: Mapped["User"] = relationship("User", back_populates = "favorite")
    person: Mapped["People"] = relationship("People", back_populates = "favorited_by")



    def serialize(self):
        return {
            "id": self.id,
            "personaje": self.person.serialize()

            
        }
    
class Nave(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    tipo: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    dimension: Mapped[int] = mapped_column(nullable=False)
        
    favorited_nave_by: Mapped[list["Favorite_nave"]] = relationship(
        "Favorite_nave", 
        back_populates = "nave"
    )
    
    def serialize(self):
        return {
            "id": self.id,
            "tipo": self.tipo,
            "description": self.description,
        }
    
class Favorite_nave(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
   
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    nave_id: Mapped[int] = mapped_column(ForeignKey("nave.id"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates = "favorite_nave")
    nave: Mapped["Nave"] = relationship("Nave", back_populates = "favorited_nave_by")

    def serialize(self):
        return {
            "id": self.id,
            "nave": self.nave.serialize()
        }
    