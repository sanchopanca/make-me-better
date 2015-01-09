from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy import Integer, String, Text, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from flask_login import UserMixin

from mmb import hashing

Base = declarative_base()

Session = sessionmaker()
engine = create_engine('sqlite:////tmp/db.db', echo=False)
Session.configure(bind=engine)
session = Session()


class User(Base, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String)
    name = Column(String)
    password_hash = Column(String)
    free_time = Column(Integer)
    tasks = relationship('Task', backref='user')

    def __init__(self, email, name, password):
        # TODO handle email with '+'
        self.email = email
        self.name = name
        self.password_hash = hashing.hash_password(bytes(password, encoding='utf8'),
                                                   bytes(email, encoding='utf8'))
        self.free_time = 0

    def __eq__(self, other):
        # TODO do it right
        return self.name == other.name and self.email == other.email and self.password_hash == other.password_hash

    @staticmethod
    def add(email, name, password):
        # TODO check if user's name or email already exists
        user = User(email, name, password)
        session.add(user)
        session.commit()
        return user

    @staticmethod
    def get_by_id(user_id):
        return session.query(User).filter(User.id == user_id).first()

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
    done = Column(Boolean)
    parent_task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    subtasks = relationship('Task', backref=backref('parent_task', remote_side=[id]))

    def __init__(self, user: User, name: str, description: str=None, price: int=0, parent_task=None):
        self.user = user
        self.name = name
        self.description = description
        self.price = price
        self.done = False
        self.parent_task = parent_task

    def get_subtasks(self):
        return session.query(Task).filter(Task.parent_task_id == self.id).all()

    def mark_as_done(self):
        # TODO add price to user.free_time
        if not self.done:
            self.done = True
            subtasks = self.get_subtasks()
            for task in subtasks:
                task.mark_as_done()

            if self.parent_task is not None:
                all_neighbors_are_done = True
                neighbor_tasks = self.parent_task.get_subtasks()
                for task in neighbor_tasks:
                    if not task.done:
                        all_neighbors_are_done = False
                        break

                if all_neighbors_are_done:
                    self.parent_task.mark_as_done()

    @staticmethod
    def add(name: str, description: str=None, price: int=None, parent_task=None, parent_task_id=None,
            user: User=None, user_id=None):
        if user is None and user_id is None:
            raise ValueError('You must specify user or user_id')
        if user_id is not None:
            user = User.get_by_id(user_id)
        if parent_task_id is not None:
            parent_task = Task.get_by_id(parent_task_id)
        if parent_task and parent_task.user != user:
            raise ValueError('Parent task must belong to the same user')

        task = Task(user, name, description, price, parent_task)
        session.add(task)
        session.commit()  # TODO make decorator
        return task

    @staticmethod
    def get_by_id(task_id):
        return session.query(Task).filter(Task.id == task_id).first()


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    u1 = User.add('user@example.com', 'user', 'password')
    t1 = Task.add('Task', user=u1)
    t2 = Task.add('Task2', user_id=u1.id, parent_task_id=t1.id)
    t2.mark_as_done()
    print(t1.done)
    session.flush()
