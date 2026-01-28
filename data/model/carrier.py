from data.config.base import Base
from sqlalchemy import Column, String, Integer, JSON


class Carrier(Base):

    __tablename__ = "carrier"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    marketplace = Column(String(30), nullable=True)    
    asanaID = Column(String(30), nullable=False)
    integrationsID = Column(JSON, nullable=True)
    icon = Column(String, nullable=False)

    def __repr__(self):
        return f"Carrier(id={self.id!r}, name={self.name!r}, marketplace={self.marketplace!r}, asanaID={self.asanaID!r}, integrationsID={self.integrationsID!r}, icon={self.icon!r})"
