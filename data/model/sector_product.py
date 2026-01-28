from data.config.base import Base
from sqlalchemy import Column, String, Integer

class SectorProduct(Base):

    __tablename__ = "sector_product"
    
    id = Column(Integer, primary_key=True)
    sku = Column(String(30), nullable=False, unique=True)
    sector = Column(String(30), nullable=False)
    historic = Column(String, nullable=True)


    def __repr__(self):
        return f"SectorProduct(id={self.id!r}, sku={self.sku!r}, sector={self.sector!r}, historic={self.historic!r})"
