from data.config.connection import DBConnectionHandler
from data.model.commentsV2 import CommentsV2 as Comments
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import null

class CommentsV2Repository:

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

    def insert(self, sign:str, module:str, reference:str, user:str, date, type_msg:str, text:str=null(), sticker:str=null(), image:str=null(), audio:str=null(), video:str=null(), attachment:str=null(), reply:int=null()):
        with DBConnectionHandler() as db:
            try:
                data_insert = Comments(sign=sign, module=module, reference=reference, user=user, date=date, type_msg=type_msg, text=text, sticker=sticker, image=image, audio=audio, video=video, attachment=attachment, reply=reply)
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
