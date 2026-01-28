from data.config.base import Base
from sqlalchemy import Column, String, Integer, JSON, Boolean


class Company(Base):

    __tablename__ = "company"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    razao = Column(String, nullable=False)
    cnpj = Column(String(14), nullable=False, unique=True)    
    ie = Column(String(20), nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(JSON, nullable=False)
    active = Column(Boolean, nullable=False)
    icon = Column(String, nullable=True)
    asanaID = Column(String(30), nullable=False, unique=True)


    def __repr__(self):
        return f"Company(id={self.id!r}, name={self.name!r}, razao={self.razao!r}, cnpj={self.cnpj!r}, ie={self.ie!r}, phone={self.phone!r}, address={self.address!r}, active={self.active!r}, icon={self.icon!r}, asanaID={self.asanaID!r})"
