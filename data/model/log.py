from data.config.base import Base
from sqlalchemy import Column, String, Integer, Date


class Log(Base):

    __tablename__ = "log"

    id = Column(Integer, primary_key=True)
    data = Column(Date, index=True, nullable=False)
    user =  Column(String(30), nullable=True)
    session =  Column(String(50), nullable=True)
    log = Column(String, nullable=False)


    def __repr__(self):
        return f"Log(id={self.id!r}, date={self.date!r}, user={self.user!r}, session={self.session!r}, log={self.log!r})"
