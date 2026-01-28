from data.config.connection import DBConnectionHandler
from data.model.order_product import OrderProduct
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import text

class OrderProductRepository:

    def filter_number(self, number):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(OrderProduct).filter(OrderProduct.order_number==number).all()
                return data
            except NoResultFound:
                return None

    def filter_name(self, name):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(OrderProduct).filter(OrderProduct.name==name).all()
                return data
            except NoResultFound:
                return None

    def filter_sku(self, sku):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(OrderProduct).order_by(text("id desc")).filter(OrderProduct.sku==sku).first()
                return data
            except NoResultFound:
                return None

    def insert(self, order_number, name, sku, qty, icon, customization):
        with DBConnectionHandler() as db:
            try:
                data_insert = OrderProduct(order_number=order_number, name=name, sku=sku, qty=qty, icon=icon, customization=customization)
                db.session.add(data_insert)
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def delete(self, id):
        with DBConnectionHandler() as db:
            try:
                db.session.query(OrderProduct).filter(OrderProduct.id==id).delete()
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def update(self, id, fild, data):
        with DBConnectionHandler() as db:
            try:
                db.session.query(OrderProduct).filter(OrderProduct.id==id).update({fild:data})
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception
