from data.config.base import Base
from sqlalchemy import Column, String, Integer


class WarrantyProduct(Base):

    __tablename__ = "warranty_product"

    id = Column(Integer, primary_key=True)
    sign = Column(String, nullable=False)
    order_ref = Column(String, nullable=False)

    name = Column(String, nullable=False)
    sku = Column(String(30), nullable=False)
    qty = Column(Integer, nullable=False)
    icon = Column(String, nullable=False)

    customization = Column(String, nullable=True)
    note = Column(String, nullable=True)
