import os
from data.repository.api_platforms import API_PlatformsRepository as API_ACCESS
from flet.security import decrypt, encrypt
from dotenv import load_dotenv
load_dotenv(dotenv_path="controllers/.env")


class API:
    """" Interface para implantação das integrações de APIs. """

    def __init__(self, developer_account:str, api_platform:str) -> None:

        self.api_platform = api_platform
        self.developer_account = developer_account



    def get_access(self) -> None:
        """ Obtem as informações de acesso da api salvas no sistema. """

        try:
            get_access_info = API_ACCESS().query(platform=self.api_platform, developer_account=self.developer_account)
            #print(f'\n🐞 API > get_access() ==> GET ACCESS INFO: {get_access_info}\n') ##DEBUG

            self.integration_id = get_access_info.id
            self.api_production_environment = get_access_info.api_production_environment
            self.api_test_environment = get_access_info.api_test_environment
            self.api_version = get_access_info.api_version
            self.user_account = None if get_access_info.user_account is None else get_access_info.user_account
            self.login_user = None if get_access_info.login_user is None else self.__decrypt(get_access_info.login_user)
            self.login_passwd = None if get_access_info.login_passwd is None else self.__decrypt(get_access_info.login_passwd)
            self.access_code = None if get_access_info.access_code is None else self.__decrypt(get_access_info.access_code)
            self.access_token = None if get_access_info.access_token is None else self.__decrypt(get_access_info.access_token)
            self.access_token_refresh = None if get_access_info.access_token_refresh is None else self.__decrypt(get_access_info.access_token_refresh)
            self.access_token_expiration = None if get_access_info.access_token_expiration is None else self.__decrypt(get_access_info.access_token_expiration)
            self.test_access_code = None if get_access_info.test_access_code is None else self.__decrypt(get_access_info.test_access_code)
            self.test_access_token = None if get_access_info.test_access_token is None else self.__decrypt(get_access_info.test_access_token)
            self.test_access_token_refresh = None if get_access_info.test_access_token_refresh is None else self.__decrypt(get_access_info.test_access_token_refresh)
            self.test_access_token_expiration = None if get_access_info.test_access_token_expiration is None else self.__decrypt(get_access_info.test_access_token_expiration)
            self.app_id = None if get_access_info.app_id is None else self.__decrypt(get_access_info.app_id)
            self.app_key = None if get_access_info.app_key is None else self.__decrypt(get_access_info.app_key)
            self.app_key_expiration = None if get_access_info.app_key_expiration is None else self.__decrypt(get_access_info.app_key_expiration)
            self.test_app_id = None if get_access_info.test_app_id is None else self.__decrypt(get_access_info.test_app_id)
            self.test_app_key = None if get_access_info.test_app_key is None else self.__decrypt(get_access_info.test_app_key)
            self.test_app_key_expiration = None if get_access_info.test_app_key_expiration is None else self.__decrypt(get_access_info.test_app_key_expiration)
            self.description = get_access_info.description
            self.active = get_access_info.active

        except Exception as exc:
            print(f'\n❌ API > get_access() ==> EXCEPTION: {exc}\n')
            return None


    def update_access(self, new_access_token:str, new_refresh_token:str) -> None:
        """ Atualiza os tokens de acesso da api salvas no sistema. """

        try:
            API_ACCESS().update(id = self.integration_id, fild = "access_token", data = new_access_token)
            API_ACCESS().update(id = self.integration_id, fild = "access_token_refresh", data = new_refresh_token)
            self.access_token = new_access_token
            self.access_token_refresh = new_refresh_token

        except Exception as exc:
            print(f'\n❌ API > update_access() ==> EXCEPTION: {exc}\n')
            return None


    def update_only_access_token(self, new_access_token:str) -> None:
        """ Atualiza somente o token de acesso da api salva no sistema. """

        try:
            API_ACCESS().update(id = self.integration_id, fild = "access_token", data = new_access_token)
            self.access_token = new_access_token

        except Exception as exc:
            print(f'\n❌ API > update_only_access_token() ==> EXCEPTION: {exc}\n')
            return None


    def update_login(self, new_login_user:str, new_login_passwd:str) -> None:
        """ Atualiza os dados de login da api salvas no sistema. """

        try:
            API_ACCESS().update(id = self.integration_id, fild = "login_user", data = new_login_user)
            API_ACCESS().update(id = self.integration_id, fild = "login_passwd", data = new_login_passwd)
            self.login_user = new_login_user
            self.login_passwd = new_login_passwd

        except Exception as exc:
            print(f'\n❌ API > update_login() ==> EXCEPTION: {exc}\n')
            return None



    ## DATA ENCRYPTION  ------

    def __decrypt(self, value:str) -> str:
        """ Descriptografa dados usando a chave secreta. """

        try:
            secret_key = os.environ["secret_key"]
            decrypt_data = decrypt(value, secret_key)
            return decrypt_data

        except Exception as exc:
            print(f'\n❌ SHOPEE_API > __decrypt() ==> EXCEPTION IN DESCRYPTION: {exc}\n') ##DEBUG
            return None


    def __encrypt(self, value:str) -> str:
        """ Encriptografa dados usando a chave secreta. """

        try:
            secret_key = os.environ["secret_key"]
            encrypted = encrypt(value, secret_key)
            return encrypted

        except Exception as exc:
            print(f'\n❌ SHOPEE_API > __encrypt() ==> EXCEPTION IN ENCRYPTION: {exc}\n') ##DEBUG
            return None

    ## ------
