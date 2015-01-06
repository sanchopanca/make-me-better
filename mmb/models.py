from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
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


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=True)
    parent_task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)

    subtasks = relationship('Task', backref=backref('parent_task', remote_side=[id]))

    def __init__(self, name=None, description=None, price=None, parent_task=None):
        self.name = name
        self.description = description
        self.price = price
        self.parent_task = parent_task


Session = sessionmaker()
engine = create_engine('sqlite:////tmp/db.db', echo=True)
Session.configure(bind=engine)


session = Session(autocommit=True)


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    t1 = Task(name='t1')
    t2 = Task(name='t2', parent_task=t1)
    session.add(t1)
    session.add(t2)
    session.flush()