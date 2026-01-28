from data.config.connection import DBConnectionHandler
from data.model.notice import Notice
from sqlalchemy.orm.exc import NoResultFound

class NoticeRepository:

    def filter_id(self, id):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Notice).filter(Notice.id==id).one()
                return data
            except NoResultFound:
                return None

    def filter_all(self):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Notice).all()
                return data
            except NoResultFound:
                return None

    def insert(self, date, user:str, topic:str, title:str, messagem:str, action:str, link:str):
        with DBConnectionHandler() as db:
            try:
                data_insert = Notice(
                    date=date,
                    user=user,
                    topic=topic,
                    title=title,
                    messagem=messagem,
                    action=action,
                    link=link
                )
                db.session.add(data_insert)
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def delete(self, id):
        with DBConnectionHandler() as db:
            try:
                db.session.query(Notice).filter(Notice.id==id).delete()
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def update(self, id, fild, value):
        with DBConnectionHandler() as db:
            try:
                db.session.query(Notice).filter(Notice.id==id).update({fild:value})
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception
