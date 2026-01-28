from data.config.connection import DBConnectionHandler
from data.model.integration import Integration
from sqlalchemy.orm.exc import NoResultFound


class IntegrationRepository:

    def filter_id(self, id):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Integration).filter(Integration.id==id).one()
                return data
            except NoResultFound:
                return None 

    def filter_name(self, name):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Integration).filter(Integration.name==name).one()
                return data
            except NoResultFound:
                return None
            
    def filter_all(self):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Integration).all()
                return data
            except NoResultFound:
                return None

    def insert(self, name, group, multiple, icon):
        with DBConnectionHandler() as db:
            try:
                data_insert = Integration(
                    name=name,
                    group=group,
                    multiple=multiple,
                    icon=icon
                )
                db.session.add(data_insert)
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def delete(self, id):
        with DBConnectionHandler() as db:
            try:
                db.session.query(Integration).filter(Integration.id==id).delete()
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def update(self, id, fild, data):
        with DBConnectionHandler() as db:
            try:
                db.session.query(Integration).filter(Integration.id==id).update({fild:data})
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception
