from data.config.connection import DBConnectionHandler
from data.model.log import Log
from sqlalchemy.orm.exc import NoResultFound

class LogRepository:

    def filter_id(self, id):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Log).filter(Log.id==id).one()
                return data
            except NoResultFound:
                return None

    def filter_all(self):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Log).all()
                return data
            except NoResultFound:
                return None        

    def insert(self, data, user, session, log):
        with DBConnectionHandler() as db:
            try:
                data_insert = Log(
                    data=data,
                    user=user,
                    session=session,
                    log=log
                )
                db.session.add(data_insert)
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def delete(self, id):
        with DBConnectionHandler() as db:
            try:
                db.session.query(Log).filter(Log.id==id).delete()
                db.session.commit() 
            except Exception as exception:
                db.session.rollback()
                raise exception                 

    def update(self, id, fild, value):
        with DBConnectionHandler() as db:
            try:
                db.session.query(Log).filter(Log.id==id).update({fild:value})
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception                                      
