from data.config.connection import DBConnectionHandler
from data.model.orderV2 import OrderV2 as Order
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.sql import text

from controllers.date_control import date_differenceCALC as CALC

class OrderRepositoryV2:

    def filter_id(self, id):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Order).filter(Order.id==id).one()
                return data
            except NoResultFound:
                return None

    def filter_status(self, status:str):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Order).filter(Order.order_status==status).all()
                return data
            except NoResultFound:
                return None

    def filter_number(self, number):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Order).filter(Order.order_number==number).one()
                return data
            except NoResultFound:
                return None
            except MultipleResultsFound:
                data = db.session.query(Order).filter(Order.order_number==number).all()
                return data

    def filter_reference(self, ref):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Order).filter(Order.order_reference==ref).one()
                return data
            except NoResultFound:
                return None
            except MultipleResultsFound:
                data = db.session.query(Order).filter(Order.order_reference==ref).one()
                return data

    def filter_channel(self, channel):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Order).order_by(text("id desc")).filter(Order.order_channel==channel)
                return data
            except NoResultFound:
                return None

    def filter_customer(self, customer):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Order).filter(Order.order_customer.like(f'%{customer}%')).all()
                return data
            except NoResultFound:
                return None

    def filter_shippingMethod(self, metod):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Order).filter(Order.order_shippingMethod==metod).one()
                return data
            except NoResultFound:
                return

    def filter_dateCreate(self, days:int):
        date = CALC(days)
        print(date)
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Order).filter(Order.order_date.between(date["final"], date["initial"])).all()
                return data
            except NoResultFound:
                return

    def filter_dateImport(self, days:int):
        date = CALC(days)
        print(date)
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Order).filter(Order.order_dateImport.between(date["final"], date["initial"])).all()
                return data
            except NoResultFound:
                return

    def filter_ShippingDate(self, days:int):
        date = CALC(days)
        print(date)
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Order).filter(Order.order_shippingDate.between(date["final"], date["initial"])).all()
                return data
            except NoResultFound:
                return

    def filter_asanaID(self, id:str):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Order).filter_by(Order.order_task)
                return data
            except NoResultFound:
                return

    def filter_all(self):
        with DBConnectionHandler() as db:
            data = db.session.query(Order).order_by(text("id desc"))
            return data


    def insert(self, order_status, order_dateImport, order_userSystem, order_number, order_reference, order_channel, order_company, order_date, order_customer, order_customerID, order_customerNickname, order_customerPhone, order_customerEmail, order_shippingAddress, order_shippingMethod, order_shippingDate, order_shippingDateMKP, order_shippingTracking, order_task, order_historic):
        with DBConnectionHandler() as db:
            try:
                data_insert = Order(
                    order_status=order_status,
                    order_dateImport=order_dateImport,
                    order_userSystem=order_userSystem,
                    order_number=order_number,
                    order_reference=order_reference,
                    order_channel=order_channel,
                    order_company=order_company,
                    order_date=order_date,
                    order_customer=order_customer,
                    order_customerID=order_customerID,
                    order_customerNickname=order_customerNickname,
                    order_customerPhone=order_customerPhone,
                    order_customerEmail=order_customerEmail,
                    order_shippingAddress=order_shippingAddress,
                    order_shippingMethod=order_shippingMethod,
                    order_shippingDate=order_shippingDate,
                    order_shippingDateMKP=order_shippingDateMKP,
                    order_shippingTracking=order_shippingTracking,
                    order_task=order_task,
                    order_historic=order_historic
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
                db.session.query(Order).filter(Order.id==id).delete()
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def update(self, id, fild, data):
        with DBConnectionHandler() as db:
            try:
                db.session.query(Order).filter(Order.id==id).update({fild:data})
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception
