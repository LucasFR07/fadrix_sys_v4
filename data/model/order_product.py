from data.config.base import Base
from sqlalchemy import Column, String, Integer


class OrderProduct(Base):

    __tablename__ = "order_product"
    
    id = Column(Integer, primary_key=True)
    order_number = Column(String(30), nullable=False)
    name = Column(String, nullable=False)
    sku = Column(String(30), nullable=False)
    qty = Column(Integer, nullable=False)
    icon = Column(String, nullable=True)
    customization = Column(String, nullable=True)
    

    def __repr__(self):
        return f"ProductOrder(id={self.id!r}, order_number={self.order_number!r}, name={self.name!r}, sku={self.sku!r}, qty={self.qty!r}, icon={self.icon!r}, customization={self.customization!r})"
