from data.config.connection import DBConnectionHandler
from data.model.saleschannel import SalesChannel
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import text



class SalesChannelRepository:

    def filter_id(self, id):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(SalesChannel).filter(SalesChannel.id==id).one()
                return data 
            except NoResultFound:
                return None 

    def filter_name(self, name):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(SalesChannel).filter(SalesChannel.name==name).first()
                return data 
            except NoResultFound:
                return None

    def filter_all(self):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(SalesChannel).all()
                return data 
            except NoResultFound:
                return None               

    def filter_ideris(self, id):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(SalesChannel).filter(SalesChannel.iderisID==id).one()
                return data 
            except NoResultFound:
                return None 

    def filter_tiny(self, id):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(SalesChannel).filter(SalesChannel.tinyID==id).one()
                return data 
            except NoResultFound:
                return None

    def filter_marketplace(self, name):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(SalesChannel).filter(SalesChannel.name==name).all()
                return data 
            except NoResultFound:
                return None

    def insert(self, name, company, icon, asanaID, iderisID, tinyID):
        with DBConnectionHandler() as db:
            try:
                data_insert = SalesChannel(
                    name=name,
                    company=company,
                    icon=icon,
                    asanaID=asanaID,
                    iderisID=iderisID,
                    tinyID=tinyID
                )
                db.session.add(data_insert)
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def delete(self, id):
        with DBConnectionHandler() as db:
            try:
                db.session.query(SalesChannel).filter(SalesChannel.id==id).delete()
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def update(self, id, fild, data):
        with DBConnectionHandler() as db:
            try:
                db.session.query(SalesChannel).filter(SalesChannel.id==id).update({fild:data})
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception
