from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

from flask_login import UserMixin

from mmb import hashing

Base = declarative_base()


class User(Base, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String)
    name = Column(String)
    password_hash = Column(String)

    def __init__(self, email, name, password):
        self.email = email
        self.name = name
        self.password_hash = hashing.hash_password(bytes(password, encoding='utf8'),
                                                   bytes(email, encoding='utf8'))