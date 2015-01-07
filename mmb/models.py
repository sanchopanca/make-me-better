from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from flask_login import UserMixin

from mmb import hashing

Base = declarative_base()

Session = sessionmaker()
engine = create_engine('sqlite:////tmp/db.db', echo=True)
Session.configure(bind=engine)
session = Session(autocommit=True)


class User(Base, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String)
    name = Column(String)
    password_hash = Column(String)

    tasks = relationship('Task', backref='user')

    def __init__(self, email, name, password):
        # TODO handle email with '+'
        self.email = email
        self.name = name
        self.password_hash = hashing.hash_password(bytes(password, encoding='utf8'),
                                                   bytes(email, encoding='utf8'))

    def __eq__(self, other):
        # TODO do it right
        return self.name == other.name and self.email == other.email and self.password_hash == other.password_hash

    @staticmethod
    def login(email, password):
        # TODO Do not allow login more often than 1 time per N seconds
        password_hash = hashing.hash_password(bytes(password, encoding='utf8'),
                                              bytes(email, encoding='utf8'))
        return session.query(User).filter(User.email == email, User.password_hash == password_hash).first()


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=True)
    parent_task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    subtasks = relationship('Task', backref=backref('parent_task', remote_side=[id]))

    def __init__(self, user, name=None, description=None, price=None, parent_task=None):
        self.user = user
        self.name = name
        self.description = description
        self.price = price
        self.parent_task = parent_task


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    u1 = User('user@example.com', 'user', 'password')
    u2 = User.login('user@example.com', 'password')
    print(u1 == u2)
    t1 = Task(u1, name='t1')
    t2 = Task(u1, name='t2', parent_task=t1)
    session.add(t1)
    session.add(t2)
    session.flush()
