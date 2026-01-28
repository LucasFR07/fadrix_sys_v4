from data.config.base import Base
from sqlalchemy import Column, String, Integer, DateTime


class ChatID(Base):

    __tablename__ = "chatID"

    id = Column(Integer, primary_key=True)
    order_number = Column(String(30), nullable=False)
    order_channel = Column(String(30), nullable=False)
    order_company = Column(String(30), nullable=False)
    userID = Column(Integer, nullable=False)
    user_nick = Column(String(30), nullable=False)
    conversation_id = Column(String(30), nullable=False)
    message = Column(String, nullable=False)
    user_system = Column(String(30), nullable=False)
    date = Column(DateTime, index=True, nullable=False)


    def __repr__(self):
        return f"Chat(id={self.id!r}, order_number={self.order_number!r}, order_channel={self.order_channel!r}, order_company={self.order_company!r}, userID={self.userID!r}, user_nick={self.user_nick!r}, conversation_id={self.conversation_id!r}, message={self.message!r}, user_system={self.user_system!r}, date={self.date!r})"
