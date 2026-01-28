from data.config.base import Base
from sqlalchemy import Column, String, Integer, JSON, Date


class Quotation(Base):

    __tablename__ = "quotation"
    
    id = Column(Integer, primary_key=True)
    status = Column(String(30), nullable=True)
    user = Column(String(30), nullable=False)
    date = Column(Date, index=True, nullable=False)    
    quote_number = Column(String(30), nullable=False, unique=True)
    quote_reference = Column(String(30), nullable=True)   
    quote_gateway = Column(String(30), nullable=False)
    origin_address = Column(JSON, nullable=False)
    destination_address = Column(JSON, nullable=False)
    packing = Column(JSON, nullable=False)
    carrier = Column(JSON, nullable=False)


    def __repr__(self):
        return f"Quotation(id={self.id!r}, status={self.status!r}, user={self.user!r}, date={self.date!r}, quote_number={self.quote_number!r}, quote_reference={self.quote_reference!r}, quote_gateway={self.quote_gateway!r}, origin_address={self.origin_address!r}, destination_address={self.destination_address!r}, packing={self.packing!r}, carrier={self.carrier!r})"
