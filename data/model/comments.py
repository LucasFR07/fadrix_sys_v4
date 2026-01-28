from data.config.base import Base
from sqlalchemy import Column, String, Integer, DateTime


class Comments(Base):

    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True)
    module = Column(String(30), nullable=False)
    reference = Column(String(30), nullable=False)
    text = Column(String, nullable=False)
    user = Column(String(30), nullable=False)
    date = Column(DateTime, index=True, nullable=False)


    def __repr__(self):
        return f"Comments(id={self.id!r}, module={self.module!r}, reference={self.reference!r}, text={self.text!r}, user={self.user!r}, date={self.date!r})"
