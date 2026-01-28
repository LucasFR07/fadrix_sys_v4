from data.config.base import Base
from sqlalchemy import Column, String, Integer


class Status(Base):

    __tablename__ = "status"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False, unique=True)
    module = Column(String(30), nullable=False)
    color = Column(String(30), nullable=False)
    asanaID = Column(String(30), nullable=True)

    def __repr__(self):
        return f"Status(id={self.id!r}, name={self.name!r}, module={self.module!r}, color={self.color!r}, asanaID={self.asanaID!r})"
