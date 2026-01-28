from data.config.base import Base
from sqlalchemy import Column, String, Integer, DateTime


class Notice(Base):

    __tablename__ = "notice"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, index=True, nullable=False)
    user = Column(String(30), nullable=False)
    topic =  Column(String(30), nullable=False)
    title = Column(String, nullable=False)
    messagem = Column(String, nullable=False)
    action =  Column(String(30), nullable=False)
    link = Column(String, nullable=True)


    def __repr__(self):
        return f"Notice(id={self.id!r}, date={self.date!r}, user={self.user!r}, topic={self.topic!r}, title={self.title!r}, messagem={self.messagem!r}, action={self.action!r}, link={self.link!r})"
