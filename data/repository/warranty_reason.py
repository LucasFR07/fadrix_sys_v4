from data.config.connection import DBConnectionHandler
from data.model.warranty_reason import WarrantyReason
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import text


class WarrantyReasonRepository:

    def filter_id(self, id:str):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(WarrantyReason).filter(WarrantyReason.id==id).one()
                return data
            except NoResultFound:
                return None

    def filter_reason(self, reason:str):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(WarrantyReason).filter(WarrantyReason.reason==reason).all()
                return data
            except NoResultFound:
                return None

    def filter_all(self):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(WarrantyReason).order_by(text("id desc")).all()
                return data
            except NoResultFound:
                return None

    def insert(self, reason:str, asana_id:str, active:bool):
        with DBConnectionHandler() as db:
            try:
                data_insert = WarrantyReason(
                    reason=reason,
                    asana_id=asana_id,
                    active=active
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
                db.session.query(WarrantyReason).filter(WarrantyReason.id==id).delete()
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def update(self, id, fild, data):
        with DBConnectionHandler() as db:
            try:
                db.session.query(WarrantyReason).filter(WarrantyReason.id==id).update({fild:data})
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception
