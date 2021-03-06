#!/usr/bin/python3
"""
database storage engine
"""
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy import create_engine
from models import (
    amenity,
    city,
    state,
    place,
    review,
    user,
)
from models.base_model import Base

# try to import config if available
try:
    from decouple import config as getenv
except ImportError:
    from os import getenv

# environs and options
env = {
    # environment settings to use
    'environment': getenv('HBNB_ENV'),

    # db connections
    'mysql_user': getenv('HBNB_MYSQL_USER'),
    'mysql_passwd': getenv('HBNB_MYSQL_PWD'),
    'mysql_host': getenv('HBNB_MYSQL_HOST'),
    'mysql_db': getenv('HBNB_MYSQL_DB'),
    'mysql_port': 3306,
}

# mapped each models to a dict key
models = {
    'Amenity': amenity.Amenity,
    'City': city.City,
    'User': user.User,
    'Place': place.Place,
    'Review': review.Review,
    'State': state.State
}


# class definition starts here
class DBStorage:
    """A database storage engine class
    """
    __engine = None
    __session = None

    def __init__(self):
        """instantiates engine
        """

        self.__engine = create_engine("mysql+mysqldb://{}:{}@{}:{}/{}".format(
            env['mysql_user'],
            env['mysql_passwd'],
            env['mysql_host'],
            env['mysql_port'],
            env['mysql_db']),
            pool_pre_ping=True)

        try:
            if env['environment'] == 'test':
                Base.metadata.drop_all(self.__engine)
        except KeyError:
            pass

    def all(self, cls=None):
        """retrieves all object instance

        Args:
            cls ([class.BaseModel], optional): [BaseModel model].
            Defaults to None.

        Returns:
            [dict]: Returns a dictionary of instances
        """
        objects = {}
        for mod in models:
            if cls is None or cls is models[mod] or cls is mod:
                objs = self.__session.query(models[mod]).all()
                for obj in objs:
                    key = obj.__class__.__name__ + '.' + obj.id
                    objects[key] = obj

        return objects

    def new(self, obj):
        """adds a new object to the current database session

        Args:
            obj (class.BaseModel): [description]
        """
        self.__session.add(obj)

    def save(self):
        """commits the new objects to the current database session
        """
        try:
            # try commiting
            self.__session.commit()
        except Exception:
            # if an exception occurs rollback the commit
            self.__session.rollback()
            raise
        finally:
            # end the database session
            self.__session.close()

    def delete(self, obj=None):
        """deletes a table from the database

        Args:
            obj (database table name, optional): [description].
            Defaults to None.
        """
        if obj is None:
            return

        try:
            self.__session.delete(obj)
        except Exception:
            raise

    def reload(self):
        """reloads all a objects from the database
        """
        Amenity = models['Amenity']
        City = models['City']
        User = models['User']
        Place = models['Place']
        State = models['State']

        Base.metadata.create_all(self.__engine)
        self.__session = scoped_session(sessionmaker(
            bind=self.__engine, expire_on_commit=False))

    def close(self):
        """closes all db sessions"""
        self.__session.remove()
