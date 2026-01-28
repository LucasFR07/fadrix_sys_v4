from data.config.connection import DBConnectionHandler
from data.model.userV2 import UserV2
from sqlalchemy.orm.exc import NoResultFound

import os
from flet.security import encrypt
from dotenv import load_dotenv
load_dotenv(
    dotenv_path="controllers/.env"
)


class UserV2Repository:

    def filter_id(self, id:int):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(UserV2).filter(UserV2.id==id).one()
                return data
            except NoResultFound:
                return None

    def filter_user(self, user:str):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(UserV2).filter(UserV2.user==user).one()
                return data
            except NoResultFound:
                return None

    def filter_name(self, name:str):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(UserV2).filter(UserV2.name==name).one()
                return data
            except NoResultFound:
                return None

    def filter_all(self):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(UserV2).all()
                return data
            except NoResultFound:
                return None

    def insert(self, name:str, user:str, password:str, theme_color:str, theme_light:str, photo:str, photo_skype:str, usr_group:str, usr_active:bool, usr_connected:bool, usr_session:str, asanaID:str):
        with DBConnectionHandler() as db:
            try:
                data_insert = UserV2(
                    name=name,
                    user=user,
                    password=self.__encrypt(password),
                    theme_color=theme_color,
                    theme_light=theme_light,
                    photo=photo,
                    photo_skype=photo_skype,
                    usr_group=usr_group,
                    usr_active=usr_active,
                    usr_connected=usr_connected,
                    usr_session=usr_session,
                    asanaID=asanaID
                )
                db.session.add(data_insert)
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def delete(self, id:int):
        with DBConnectionHandler() as db:
            try:
                db.session.query(UserV2).filter(UserV2.id==id).delete()
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def update(self, id:int, fild:str, data:str):
        with DBConnectionHandler() as db:
            try:
                db.session.query(UserV2).filter(UserV2.id==id).update({fild:data})
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def __encrypt(self, psw):
        secret_key = os.environ["secret_key"]
        encrypted = encrypt(psw, secret_key)
        return encrypted
