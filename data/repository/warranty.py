from data.config.connection import DBConnectionHandler
from data.model.warranty import Warranty
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import text


class WarrantyRepository:

    def filter_id(self, id:str):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Warranty).filter(Warranty.id==id).one()
                return data
            except NoResultFound:
                return None


    def filter_status(self, status:str):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Warranty).filter(Warranty.status==status).all()
                return data
            except NoResultFound:
                return None


    def filter_order(self, order:str):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Warranty).filter(Warranty.order_ref==order).all()
                return data
            except NoResultFound:
                return None


    def filter_channel(self, channel:str):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Warranty).filter(Warranty.order_channel==channel).all()
                return data
            except NoResultFound:
                return None


    def filter_order_and_sing(self, sign:str, order:str):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Warranty).filter(Warranty.order_ref==order, Warranty.sign==sign).one()
                return data
            except NoResultFound:
                return None


    def filter_all(self):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Warranty).order_by(text("id desc")).all()
                return data
            except NoResultFound:
                return None


    def insert(self, sign, status, date, user, order_ref, order_channel, order_buyer, shipping_address, shipping_method, shipping_date, shipping_tracking, reason, liable, note, task_id, historic):
        with DBConnectionHandler() as db:
            try:
                data_insert = Warranty(
                    sign=sign,
                    status=status,
                    date=date,
                    user=user,
                    order_ref=order_ref,
                    order_channel=order_channel,
                    order_buyer=order_buyer,
                    shipping_address=shipping_address,
                    shipping_method=shipping_method,
                    shipping_date=shipping_date,
                    shipping_tracking=shipping_tracking,
                    reason=reason,
                    liable=liable,
                    note=note,
                    task_id=task_id,
                    historic=historic
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
                db.session.query(Warranty).filter(Warranty.id==id).delete()
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception


    def update(self, id, fild, data):
        with DBConnectionHandler() as db:
            try:
                db.session.query(Warranty).filter(Warranty.id==id).update({fild:data})
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception
