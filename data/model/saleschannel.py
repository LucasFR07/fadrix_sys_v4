from data.config.base import Base
from sqlalchemy import Column, String, Integer, JSON


class SalesChannel(Base):

    __tablename__ = "sales_channel"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    company = Column(JSON, nullable=False)
    icon = Column(String, nullable=False)

    asanaID = Column(String(30), nullable=False)
    iderisID = Column(String(30), nullable=True)
    tinyID = Column(String(30), nullable=True)


    def __repr__(self):
        return f"SalesChannel(id={self.id!r}, name={self.name!r}, company={self.company!r}, icon={self.icon!r}, asanaID={self.asanaID!r}, iderisID={self.iderisID!r}, tinyID={self.tinyID!r})"
