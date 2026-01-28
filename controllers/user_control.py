import os
from flet.security import decrypt
from dotenv import load_dotenv
load_dotenv(
    dotenv_path="controllers/.env"
)

## CONEXÃO COM DADOS
from data.repository.user import UserRepository as USER
from data.repository.userV2 import UserV2Repository as USER2
from controllers.date_control import date_create as DATE
from sqlalchemy import null


class UserControl():

    """Controla o acesso de login e logout da conta do usuário no sistema."""

    def login(self, user:str, password:str, session:str):

        """ Validação de login e permissão de acesso. """

        self.user = user
        self.password = password

        try:
            self.login_user = USER2().filter_user(user=self.user)
            if self.login_user is not None:
                passwd = self.__decrypt(self.login_user.password)
                if self.login_user.user==self.user and passwd==self.password:
                    connected_user = USER2().update(id=self.login_user.id, fild="usr_connected", data=True)
                    session_user = USER2().update(id=self.login_user.id, fild="usr_session", data=session)

                    return {
                        "status": "ok",
                        "message": "Conectado com sucesso.",
                        "user": {
                            "id": self.login_user.id,
                            "name": self.login_user.name,
                            "user": self.login_user.user,
                            "theme_color": self.login_user.theme_color,
                            "theme_light": self.login_user.theme_light,
                            "photo": self.login_user.photo,
                            "photo_skype": self.login_user.photo_skype,
                            "usr_group": self.login_user.usr_group,
                            "usr_active": self.login_user.usr_active,
                            "usr_session": session,
                            "asanaID": self.login_user.asanaID
                        }
                    }

                else:
                    return {"status": "error", "message": "Senha Inválida."}

            else:
                return {"status": "error", "message": "Usuário não encontrado."}

        except Exception as e:
            print(f'\n❌ USER_CONTROL > login() V4 ==> EXCEPTION: {e}\n')
            return {"status": "error", "message": "Erro interno, tente novamente!"}


    def logout(self, id:str):

        """ Encerrar login e finalizar sessão. """

        try:
            id_user = id
            connected_user = USER2().update(id=id_user, fild="usr_connected", data=False)
            session_user = USER2().update(id=id_user, fild="usr_session", data=null())
            return {"Status": "ok", "Message": "Login encerrado com sucesso."}

        except Exception as e:
            print(f'\n❌ USER_CONTROL > logout() V4 ==> EXCEPTION: {e}\n')
            return {"status": "error", "message": "Erro interno, tente novamente!"}


    def __decrypt(self, psw):

        """ Descrypt password for login. """

        secret_key = os.environ["secret_key"]
        return decrypt(psw, secret_key)
