from data.config.connection import DBConnectionHandler
from data.model.reports import Reports
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import text


class ReportsRepository:

    def filter_id(self, id):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Reports).filter(Reports.id==id).one()
                return data
            except NoResultFound:
                return None

    def filter_type(self, type:str):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Reports).filter(Reports.report_type==type).all()
                return data
            except NoResultFound:
                return None

    def filter_file(self, title:str):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Reports).filter(Reports.report_title==title).one()
                return data
            except NoResultFound:
                return None

    def filter_all(self):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Reports).all()
                return data
            except NoResultFound:
                return None

    def insert(self, report_date, report_user, report_type, report_title, report_file_extension, report_path):
        with DBConnectionHandler() as db:
            try:
                data_insert = Reports(
                    report_date=report_date,
                    report_user=report_user,
                    report_type=report_type,
                    report_title=report_title,
                    report_file_extension=report_file_extension,
                    report_path=report_path
                )
                db.session.add(data_insert)
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def delete(self, id):
        with DBConnectionHandler() as db:
            try:
                db.session.query(Reports).filter(Reports.id==id).delete()
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def update(self, id, fild, data):
        with DBConnectionHandler() as db:
            try:
                db.session.query(Reports).filter(Reports.id==id).update({fild:data})
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception
