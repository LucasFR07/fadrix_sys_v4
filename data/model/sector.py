from data.config.base import Base
from sqlalchemy import Column, String, Integer, Boolean


class Sector(Base):

    __tablename__ = "sector"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False, unique=True)
    default = Column(Boolean, nullable=False)
    asanaID = Column(String(30), nullable=False, unique=True)


    def __repr__(self):
        return f"Sector(id={self.id!r}, name={self.name!r}, default={self.default!r}, asanaID={self.asanaID!r})"
