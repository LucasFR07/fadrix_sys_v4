from data.config.connection import DBConnectionHandler
from data.model.carrier import Carrier
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import text

class CarrierRepository:

    def filter_id(self, id:int):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Carrier).filter(Carrier.id==id).one()
                return data
            except NoResultFound:
                return None

    def filter_name(self, name):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Carrier).filter(Carrier.name==name).one()
                return data
            except NoResultFound:
                return None
            
    def filter_marketplace(self, marktp):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Carrier).filter(Carrier.marketplace==marktp).one()
                return data
            except NoResultFound:
                return None
            
    def filter_integration(self, intrg, cod):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Carrier).filter(text(f"CAST(integrationsID->>'{intrg}' AS VARCHAR) = {cod}")).one()
                return data
            except NoResultFound:
                return None

    def filter_all(self):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Carrier).all()
                return data
            except NoResultFound:
                return None

    def insert(self, name, marketplace, asanaID, integrationsID, icon):
        with DBConnectionHandler() as db:
            try:
                data_insert = Carrier(name=name, marketplace=marketplace, asanaID=asanaID, integrationsID=integrationsID, icon=icon)
                db.session.add(data_insert)
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception                

    def delete(self, id):
        with DBConnectionHandler() as db:
            try:
                db.session.query(Carrier).filter(Carrier.id==id).delete()
                db.session.commit() 
            except Exception as exception:
                db.session.rollback()
                raise exception

    def update(self, id, fild, value):
        with DBConnectionHandler() as db:
            try:
                db.session.query(Carrier).filter(Carrier.id==id).update({fild:value})
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception
