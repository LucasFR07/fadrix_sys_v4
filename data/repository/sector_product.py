from data.config.connection import DBConnectionHandler
from data.model.sector_product import SectorProduct
from sqlalchemy.orm.exc import NoResultFound

class SectorProductRepository:

    def filter_id(self, id:int):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(SectorProduct).filter(SectorProduct.id==id).one()
                return data 
            except NoResultFound:
                return None

    def filter_sku(self, sku:str):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(SectorProduct).filter(SectorProduct.sku==sku).one()
                return data 
            except NoResultFound:
                return None
            
    def filter_all(self):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(SectorProduct).all()
                return data 
            except NoResultFound:
                return None            
                               
    def insert(self, sku:str, sector:str, historic:str):
        with DBConnectionHandler() as db:
            try:
                data_insert = SectorProduct(
                    sku=sku,
                    sector=sector,
                    historic=historic
                )
                db.session.add(data_insert)
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def delete(self, id:int):
        with DBConnectionHandler() as db:
            try:
                db.session.query(SectorProduct).filter(SectorProduct.id==id).delete()
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def update(self, id:int, fild:str, data:str):
        with DBConnectionHandler() as db:
            try:
                db.session.query(SectorProduct).filter(SectorProduct.id==id).update({fild:data})
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception
