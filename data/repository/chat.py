from data.config.connection import DBConnectionHandler
from data.model.chat import ChatID
from sqlalchemy.orm.exc import NoResultFound

class ChatIDRepository:

    def filter_id(self, id):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(ChatID).filter(ChatID.id==id).one()
                return data
            except NoResultFound:
                return None

    def filter_order(self, number:str):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(ChatID).filter(ChatID.order_number==number).first()
                return data
            except NoResultFound:
                return None

    def insert(self, order_number, order_channel, order_company, userID, user_nick, conversation_id, message, user_system, date):
        with DBConnectionHandler() as db:
            try:
                data_insert = ChatID(
                    order_number=order_number,
                    order_channel=order_channel,
                    order_company=order_company,
                    userID=userID,
                    user_nick=user_nick,
                    conversation_id=conversation_id,
                    message=message,
                    user_system=user_system,
                    date=date
                )
                db.session.add(data_insert)
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def delete(self, id):
        with DBConnectionHandler() as db:
            try:
                db.session.query(ChatID).filter(ChatID.id==id).delete()
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def update(self, id, fild, data):
        with DBConnectionHandler() as db:
            try:
                db.session.query(ChatID).filter(ChatID.id==id).update({fild:data})
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception
