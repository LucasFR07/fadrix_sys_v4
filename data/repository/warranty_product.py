from data.config.connection import DBConnectionHandler
from data.model.warranty_product import WarrantyProduct
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import text


class WarrantyProductRepository:

    def filter_id(self, id:str):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(WarrantyProduct).filter(WarrantyProduct.id==id).one()
                return data
            except NoResultFound:
                return None

    def filter_sku(self, sku:str):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(WarrantyProduct).filter(WarrantyProduct.sku==sku).all()
                return data
            except NoResultFound:
                return None

    def filter_order_sign(self, order:str, sign:str):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(WarrantyProduct).filter(WarrantyProduct.order_ref==order, WarrantyProduct.sign==sign).all()
                return data
            except NoResultFound:
                return None

    def filter_all(self):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(WarrantyProduct).order_by(text("id desc")).all()
                return data
            except NoResultFound:
                return None

    def insert(self, sign, order_ref, name, sku, qty, icon, customization, note):
        with DBConnectionHandler() as db:
            try:
                data_insert = WarrantyProduct(
                    sign=sign,
                    order_ref=order_ref,
                    name=name,
                    sku=sku,
                    qty=qty,
                    icon=icon,
                    customization=customization,
                    note=note
                )
                db.session.add(data_insert)
                db.session.commit()
                return None

            except Exception as exception:
                db.session.rollback()
                raise exception

    def delete(self, id):
        with DBConnectionHandler() as db:
            try:
                db.session.query(WarrantyProduct).filter(WarrantyProduct.id==id).delete()
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def update(self, id, fild, data):
        with DBConnectionHandler() as db:
            try:
                db.session.query(WarrantyProduct).filter(WarrantyProduct.id==id).update({fild:data})
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception
