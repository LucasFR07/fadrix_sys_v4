from data.config.connection import DBConnectionHandler
from data.model.sector import Sector
from sqlalchemy.orm.exc import NoResultFound

class SectorRepository:

    def filter_id(self, id:int):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Sector).filter(Sector.id==id).one()
                return data
            except NoResultFound:
                return None

    def filter_name(self, name:str):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Sector).filter(Sector.name==name).one()
                return data
            except NoResultFound:
                return None
            
    def filter_default(self):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Sector).filter(Sector.default==True).one()
                return data
            except NoResultFound:
                return None 
            
    def filter_all(self):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Sector).all()
                return data 
            except NoResultFound:
                return None
                               
    def insert(self, name:str, default:bool, asanaID:str):
        with DBConnectionHandler() as db:
            try:
                data_insert = Sector(
                    name=name,
                    default=default,
                    asanaID=asanaID
                )
                db.session.add(data_insert)
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def delete(self, id:int):
        with DBConnectionHandler() as db:
            try:
                db.session.query(Sector).filter(Sector.id==id).delete()
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def update(self, id:int, fild:str, data:str):
        with DBConnectionHandler() as db:
            try:
                db.session.query(Sector).filter(Sector.id==id).update({fild:data})
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception
