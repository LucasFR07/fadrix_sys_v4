from data.config.connection import DBConnectionHandler
from data.model.api_platforms import API_Platforms
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import null

import os
from flet.security import encrypt
from dotenv import load_dotenv
load_dotenv(dotenv_path="C:/Users/marketing/Downloads/V4/V4/controllers/.env")


class API_PlatformsRepository:

    def query_id(self, id:int):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(API_Platforms).filter(API_Platforms.id==id).one()
                return data
            except NoResultFound:
                return None


    def query_name(self, platform:str):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(API_Platforms).filter(API_Platforms.api_platform==platform).all()
                return data
            except NoResultFound:
                return None


    def query(self, platform:str, developer_account:str):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(API_Platforms).filter(API_Platforms.api_platform==platform, API_Platforms.developer_account==developer_account).one()
                return data
            except NoResultFound:
                return None


    def insert(self, api_platform, api_production_environment, api_test_environment, api_version, developer_account, user_account, login_user, login_passwd, access_code, access_token, access_token_refresh, access_token_expiration, test_access_code, test_access_token, test_access_token_refresh, test_access_token_expiration, app_id, app_key, app_key_expiration, test_app_id, test_app_key, test_app_key_expiration, description, active):

        with DBConnectionHandler() as db:
            try:
                data_insert = API_Platforms(
                    api_platform = api_platform,
                    api_production_environment = api_production_environment,
                    api_test_environment = null() if api_test_environment is null() else api_test_environment,
                    api_version = api_version,
                    developer_account = null() if developer_account is null() else developer_account,
                    user_account = null() if user_account is null() else user_account,
                    login_user = null() if login_user is null() else self.__encrypt(login_user),
                    login_passwd = null() if login_passwd is null() else self.__encrypt(login_passwd),
                    access_code = null() if access_code is null() else self.__encrypt(access_code),
                    access_token = null() if access_token is null() else self.__encrypt(access_token),
                    access_token_refresh = null() if access_token_refresh is null() else self.__encrypt(access_token_refresh),
                    access_token_expiration = null() if access_token_expiration is null() else self.__encrypt(access_token_expiration),
                    test_access_code = null() if test_access_code is null() else self.__encrypt(test_access_code),
                    test_access_token = null() if test_access_token is null() else self.__encrypt(test_access_token),
                    test_access_token_refresh = null() if test_access_token_refresh is null() else self.__encrypt(test_access_token_refresh),
                    test_access_token_expiration = null() if test_access_token_expiration is null() else self.__encrypt(test_access_token_expiration),
                    app_id = null() if app_id is null() else self.__encrypt(app_id),
                    app_key = null() if app_key is null() else self.__encrypt(app_key),
                    app_key_expiration = null() if app_key_expiration is null() else self.__encrypt(app_key_expiration),
                    test_app_id = null() if test_app_id is null() else self.__encrypt(test_app_id),
                    test_app_key = null() if test_app_key is null() else self.__encrypt(test_app_key),
                    test_app_key_expiration = null() if test_app_key_expiration is null() else self.__encrypt(test_app_key_expiration),
                    description = description,
                    active = active
                )
                db.session.add(data_insert)
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception


    def delete(self, id:int):
        """ Deleta um registro do banco de dados. """

        try:
            with DBConnectionHandler() as db:
                db.session.query(API_Platforms).filter(API_Platforms.id==id).delete()
                db.session.commit()

        except Exception as exception:
            db.session.rollback()
            raise exception


    def update(self, id:int, fild:str, data):
        """ Atualiza um registro do banco de dados. """

        try:
            match fild:
                case "login_user" | "login_passwd" | "access_code" | "access_token" | "access_token_refresh" | "access_token_expiration" | "test_access_code" | "test_access_token" | "test_access_token_refresh" | "test_access_token_expiration" | "app_id" | "app_key" | "app_key_expiration" | "test_app_id" | "test_app_key" | "test_app_key_expiration":

                    with DBConnectionHandler() as db:
                        db.session.query(API_Platforms).filter(API_Platforms.id==id).update({fild:self.__encrypt(data) if data is not null() else null()})
                        db.session.commit()

                case _ :
                    with DBConnectionHandler() as db:
                        db.session.query(API_Platforms).filter(API_Platforms.id==id).update({fild:data})
                        db.session.commit()

        except Exception as exception:
            db.session.rollback()
            raise exception


    def __encrypt(self, tk:str):
        """ Criptografa o dado para salvar no banco de dados. """

        try:
            secret_key = os.environ["secret_key"]
            encrypted = encrypt(tk, secret_key)
            return encrypted

        except Exception as exception:
            raise exception
