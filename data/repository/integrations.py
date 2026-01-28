from data.config.connection import DBConnectionHandler
from data.model.integrations import Integrations
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import null

import os
from flet.security import encrypt
from dotenv import load_dotenv
load_dotenv(
    dotenv_path="D:/FADRIX/DEVELOPER/FADRIX-SYS/V4/controllers/.env"
)


class IntegrationsRepository:

    def filter_id(self, id):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Integrations).filter(Integrations.id==id).one()
                return data
            except NoResultFound:
                return None

    def filter_name(self, name):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Integrations).filter(Integrations.name==name).one()
                return data 
            except NoResultFound:
                return None

    def filter_company(self, name, company):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Integrations).filter(Integrations.name==name, Integrations.company==company).one()
                return data
            except NoResultFound:
                return None

    def insert(self, name, company, user, password, code, access_token, refresh_token, token_expiration, app_id, app_key, shop_id, description, active):
        with DBConnectionHandler() as db:
            try:
                data_insert = Integrations(
                    name=name,
                    company=null() if company is null() else company,
                    user=null() if user is null() else self.__encrypt(user),
                    password=null() if password is null() else self.__encrypt(password),
                    code=null() if code is null() else self.__encrypt(code),
                    access_token=null() if access_token is null() else self.__encrypt(access_token),
                    refresh_token=null() if refresh_token is null() else self.__encrypt(refresh_token),
                    token_expiration=null() if token_expiration is null() else self.__encrypt(token_expiration),
                    app_id=null() if app_id is null() else self.__encrypt(app_id),
                    app_key=null() if app_key is null() else self.__encrypt(app_key),
                    shop_id=null() if shop_id is null() else self.__encrypt(shop_id),
                    description=description,
                    active=active
                )
                db.session.add(data_insert)
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception                

    def delete(self, id):
        with DBConnectionHandler() as db:
            try:
                db.session.query(Integrations).filter(Integrations.id==id).delete()
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def update(self, id, fild, data):
        with DBConnectionHandler() as db:
            try:
                match fild:
                    case "user" | "password" | "code":
                        pass
                db.session.query(Integrations).filter(Integrations.id==id).update({fild:data})
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def __encrypt(self, tk):
        secret_key = os.environ["secret_key"]
        encrypted = encrypt(tk, secret_key)
        return encrypted
