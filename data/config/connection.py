from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pathlib import PureWindowsPath


class DBConnectionHandler:

    def __init__(self) -> None:
        self.path_db = PureWindowsPath('C:/Users/marketing/Downloads/V4/FSYS_DB.db')
        self.path_dbTest = PureWindowsPath('C:/Users/marketing/Downloads/V4/appTeste.db')
        self.__connection_string = f"sqlite:///{self.path_db}"
        self.__engine = self.__create_database_engine()
        self.session = None

    def __create_database_engine(self):
        engine = create_engine(self.__connection_string)
        return engine

    def get_engine(self):
        return self.__engine

    def __enter__(self):
        session_make = sessionmaker(bind=self.__engine)
        self.session = session_make()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()


# Base.metadata.create_all(engine)
