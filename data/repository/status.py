from data.config.connection import DBConnectionHandler
from data.model.status import Status
from sqlalchemy.orm.exc import NoResultFound

class StatusRepository:

    def filter_id(self, id):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Status).filter(Status.id==id).one()
                return data
            except NoResultFound:
                return None

    def filter_name(self, name):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Status).filter(Status.name==name).one()
                return data
            except NoResultFound:
                return None

    def filter_module(self, mod):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Status).filter(Status.module==mod).all()
                return data
            except NoResultFound:
                return None

    def filter_all(self):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Status).all()
                return data
            except NoResultFound:
                return None        

    def insert(self, name, module, color, asanaID):
        with DBConnectionHandler() as db:
            try:
                data_insert = Status(
                    name=name,
                    module=module,
                    color=color,
                    asanaID=asanaID
                )
                db.session.add(data_insert)
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception                

    def delete(self, id):
        with DBConnectionHandler() as db:
            try:
                db.session.query(Status).filter(Status.id==id).delete()
                db.session.commit() 
            except Exception as exception:
                db.session.rollback()
                raise exception                 

    def update(self, id, fild, value):
        with DBConnectionHandler() as db:
            try:
                db.session.query(Status).filter(Status.id==id).update({fild:value})
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception                                      
