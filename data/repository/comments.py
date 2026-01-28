from data.config.connection import DBConnectionHandler
from data.model.comments import Comments
from sqlalchemy.orm.exc import NoResultFound

class CommentsRepository:

    def filter_id(self, id):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Comments).filter(Comments.id==id).one()
                return data 
            except NoResultFound:
                return None 

    def filter_reference(self, mod, ref):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Comments).filter(Comments.module==mod, Comments.reference==ref).all()
                return data 
            except NoResultFound:
                return None
            
    def filter_all(self):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Comments).all()
                return data 
            except NoResultFound:
                return None

    def insert(self, module, reference, text, user, date):
        with DBConnectionHandler() as db:
            try:
                data_insert = Comments(module=module, reference=reference, text=text, user=user, date=date)
                db.session.add(data_insert)
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def delete(self, id):
        with DBConnectionHandler() as db:
            try:
                db.session.query(Comments).filter(Comments.id==id).delete()
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def update(self, id, fild, data):
        with DBConnectionHandler() as db:
            try:
                db.session.query(Comments).filter(Comments.id==id).update({fild:data})
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception
