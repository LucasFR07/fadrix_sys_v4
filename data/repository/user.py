from data.config.connection import DBConnectionHandler
from data.model.user import User
from sqlalchemy.orm.exc import NoResultFound

import os
from flet.security import encrypt
from dotenv import load_dotenv
load_dotenv(
    dotenv_path="controllers/.env"
)


class UserRepository:

    def filter_id(self, id:int):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(User).filter(User.id==id).one()
                return data
            except NoResultFound:
                return None

    def filter_user(self, user:str):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(User).filter(User.user==user).one()
                return data
            except NoResultFound:
                return None

    def filter_name(self, name:str):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(User).filter(User.name==name).one()
                return data
            except NoResultFound:
                return None

    def filter_all(self):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(User).all()
                return data
            except NoResultFound:
                return None

    def insert(self, name:str, user:str, password:str, icon:str, theme:str, group:str, asanaID:str, active:bool, connected:bool):
        with DBConnectionHandler() as db:
            try:
                data_insert = User(
                    name=name,
                    user=user,
                    password=self.__encrypt(password),
                    icon=icon,
                    theme=theme,
                    group=group,
                    asanaID=asanaID,
                    active=active,
                    connected=connected
                )
                db.session.add(data_insert)
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def delete(self, id:int):
        with DBConnectionHandler() as db:
            try:
                db.session.query(User).filter(User.id==id).delete()
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def update(self, id:int, fild:str, data:str):
        with DBConnectionHandler() as db:
            try:
                db.session.query(User).filter(User.id==id).update({fild:data})
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def __encrypt(self, psw):
        secret_key = os.environ["secret_key"]
        encrypted = encrypt(psw, secret_key)
        return encrypted
